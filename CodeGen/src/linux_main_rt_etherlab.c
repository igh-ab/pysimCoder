#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>
#include <fcntl.h>
#include <pthread.h>

#ifdef CG_WITH_IOPL
#include <sys/io.h>
#endif

#ifdef PDSERV
#include <pdserv.h>
#endif

#ifdef CANOPEN
void canopen_synch(void);
#endif

#define XNAME(x,y)  x##y
#define NAME(x,y)   XNAME(x,y)

int NAME(MODEL,_init)(void);
int NAME(MODEL,_isr)(double);
int NAME(MODEL,_end)(void);
double NAME(MODEL,_get_tsamp)(void);

#define NSEC_PER_SEC    1000000000
#define USEC_PER_SEC	1000000

static volatile int end = 0;
static double T = 0.0;
static double Tsamp;

/* Options presettings */
static char rtversion[] = "0.9";
static int prio = 99;
static int verbose = 0;
static int wait = 0;
static int extclock = 0;
double FinalTime = 0.0;

#ifdef PDSERV
struct pdserv* pdserv = NULL;
struct pdtask* pdtask = NULL;
unsigned int overruns = 0;

#define MAX_SAFE_STACK (8 * 1024) /** The maximum stack size which is
                                    guranteed safe to access without faulting.
                                   */
#define DIFF_NS(A, B) (((long long) (B).tv_sec - (A).tv_sec) * NSEC_PER_SEC \
        + (B).tv_nsec - (A).tv_nsec)

/** Return the current system time.
 * This is a callback needed by pdserv.
 */

int pd_gettime(struct timespec *time)

{

    return clock_gettime(CLOCK_REALTIME, time);

}

/** Cause a stack fault before entering cyclic operation.
 */
void stack_prefault(void)
{
    unsigned char dummy[MAX_SAFE_STACK];

    memset(dummy, 0, MAX_SAFE_STACK);
}


#endif

double get_run_time(void)
{
  return(T);
}

double get_Tsamp(void)
{
  return(Tsamp);
}

int get_priority_for_com(void)
{
  if (prio < 0)
    {
      return -1;
    }
  else
    {
      return prio - 1;
    }
}

static inline void tsnorm(struct timespec *ts)
{
  while (ts->tv_nsec >= NSEC_PER_SEC) {
    ts->tv_nsec -= NSEC_PER_SEC;
    ts->tv_sec++;
  }
}

static inline double calcdiff(struct timespec t1, struct timespec t2)
{
  long diff;
  diff = USEC_PER_SEC * ((long) t1.tv_sec - (long) t2.tv_sec);
  diff += ((int) t1.tv_nsec - (int) t2.tv_nsec) / 1000;
  return (1e-6*diff);
}

static void *rt_task(void *p)
{
  struct timespec t_next, t_current, t_isr, T0;
#ifdef PDSERV
  struct timespec start_time, last_start_time;
  struct timespec end_time;
  double cycle_time, exec_time;

#endif

  Tsamp = NAME(MODEL,_get_tsamp)();

  t_isr.tv_sec =  0L;
  t_isr.tv_nsec = (long)(1e9*Tsamp);
  tsnorm(&t_isr);

  T=0;

  NAME(MODEL,_init)();

#ifdef PDSERV
  {
    int ret = pdserv_prepare(pdserv);
    if (ret) {
        print("Failed to prepare pdserv.");
        exit(1);
    }
  }
#endif

  mlockall(MCL_CURRENT | MCL_FUTURE);

  /* Provoke the first stack fault before cyclic operation. */
  stack_prefault();


  struct sched_param param;

  if (prio >= 0) {
    param.sched_priority = prio;
    if(sched_setscheduler(0, SCHED_FIFO, &param)==-1) {
      perror("sched_setscheduler failed");
    }
  }


#ifdef CANOPEN
  canopen_synch();
#endif
  
  /* get current time */
  clock_gettime(CLOCK_MONOTONIC,&t_current);
  T0 = t_current;

#ifdef PDSERV
  last_start_time = t_current;
#endif

  while(!end){

    /* periodic task */
    T = calcdiff(t_current,T0);
#ifdef PDSERV
    clock_gettime(CLOCK_MONOTONIC,&start_time);
#endif
    NAME(MODEL,_isr)(T);
#ifdef PDSERV
    clock_gettime(CLOCK_MONOTONIC,&t_current);
#endif

#ifdef CANOPEN
    canopen_synch();
#endif

    if((FinalTime >0) && (T >= FinalTime)) break;

    t_next.tv_sec = t_current.tv_sec + t_isr.tv_sec;
    t_next.tv_nsec = t_current.tv_nsec + t_isr.tv_nsec;
    tsnorm(&t_next);

    /* Check if Overrun */
    clock_gettime(CLOCK_MONOTONIC,&t_current);
    if (t_current.tv_sec > t_next.tv_sec ||
	(t_current.tv_sec == t_next.tv_sec && t_current.tv_nsec > t_next.tv_nsec)) {
      int usec = (t_current.tv_sec - t_next.tv_sec) * 1000000 + (t_current.tv_nsec -
								 t_next.tv_nsec)/1000;
      fprintf(stderr, "Base rate overrun by %d us\n", usec);
      t_next= t_current;
    }

#ifdef PDSERV
    /* Call at end of calculation task, so that pdserv updates itself */
    pdserv_update(pdtask, &t_current);
    /* Calculate timing statistics */
    cycle_time = 1.0e-9 * DIFF_NS(last_start_time, start_time);
    exec_time  = 1.0e-9 * DIFF_NS(last_start_time, end_time);
    last_start_time = start_time;
    pdserv_update_statistics(pdtask, exec_time, cycle_time, overruns);
    clock_gettime(CLOCK_MONOTONIC, &end_time);
    overruns += DIFF_NS(t_next, end_time) > 0;
#endif

    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, NULL);
    t_current = t_next;
  }
  NAME(MODEL,_end)();
  pthread_exit(0);
}

void endme(int n)
{
  end = 1;
}

void print_usage(void)
{
  puts(  "\nUsage:  'RT-model-name' [OPTIONS]\n"
         "\n"
         "OPTIONS:\n"
         "  -h  print usage\n"
	 "  -f <final time> set the final time of the execution\n"
	 "  -v  verbose output\n"
	 "  -p <priority>  set rt task priority (default 99)\n"
	 "  -e  external clock\n"
	 "  -w  wait to start\n"
	 "  -V  print version\n"
   "  -D  command line parameters\n"
   "        SHV_BROKER=hostname:port\n"
	 "\n");
}

char *parse_string(char ** str, int parse_char)
{
  char *p = strdup(*str);
  char *r = p;
  char *s = strchr(r, parse_char);
  char *t = r;

  if (s == NULL)
    {
      return p;
    }

  *s = '\0';
  r = s + 1;

  *str = r;

  return t;
}

static void proc_opt(int argc, char *argv[])
{
  int i;
  char *t;

  while((i=getopt(argc,argv,"D:ef:hp:vVw"))!=-1){
    switch(i){
    case 'h':
      print_usage();
      exit(0);
      break;
    case 'p':
      prio = atoi(optarg);
      break;
    case 'v':
      verbose = 1;
      break;
    case 'e':
      extclock = 1;
      break;
    case 'w':
      wait = 1;
      break;
    case 'V':
      printf("Version %s\n",rtversion);
      exit(0);
      break;
    case 'f':
      if (strstr(optarg, "inf")) {
        FinalTime = 0.0;
      } else if ((FinalTime = atof(optarg)) <= 0.0) {
        printf("-> Invalid final time.\n");
        exit(1);
      }
      break;
    case 'D':
      t = parse_string(&optarg, '=');
      if (t == NULL)
        {
          break;
        }
      if (strcmp(t, "SHV_BROKER") == 0)
        {
          t = parse_string(&optarg, ':');
          if (t == NULL)
            {
              break;
            }
          setenv("SHV_BROKER_IP", t, 1);
          t = parse_string(&optarg, ':');
          if (t == NULL)
            {
              break;
            }
          setenv("SHV_BROKER_PORT", t, 1);
        }
      else
        {
          setenv(t, optarg, 1);
        }
      break;
    }
  }
}

int main(int argc,char** argv)
{
  pthread_t thrd;
  int fd;
  int uid;

  proc_opt(argc, argv);

  signal(SIGINT,endme);
  signal(SIGKILL,endme);

#ifdef CG_WITH_NRT
  uid = geteuid();
  if (uid!=0){
    fd=open("/dev/nrt",O_RDWR);
    if (fd<0){
      printf("This SW needs superuser privilegies to run!\n");
      exit(1);
    }
    close(fd);
  }
#endif /*CG_WITH_NRT*/

#ifdef CG_WITH_IOPL
  iopl(3);
#endif /*CG_WITH_IOPL*/

#ifdef PDSERV
  /* Create a pdserv instance */
  if (!(pdserv = pdserv_create("pysimcoder", "1.234", pd_gettime))) {
    printf("Failed to init pdserv.");
    exit(1);
  }
  /* Create a task */
  if (!(pdtask = pdserv_create_task(pdserv, 1.0e-9*NAME(MODEL,_get_tsamp)(), NULL))) {
    printf("Failed to create task.");
    exit(1);
  }
#endif

  pthread_create(&thrd,NULL,rt_task,NULL);

  pthread_join(thrd,NULL);

#ifdef PDSERV
  /* Clean up */
  pdserv_exit(pdserv);
#endif

  return(0);
}

