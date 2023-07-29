#include <pdserv.h>

#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <getopt.h>     // getopt()
#include <unistd.h>     // getopt()
#include <string.h>     // memset(), strcmp(), strerror()
#include <time.h>       // clock_gettime(), clock_nanosleep()
#include <sys/mman.h>   // mlockall()
#include <sched.h>      // sched_setscheduler()
#include <stdlib.h>     // strtoul(), exit()
#include <pthread.h>    // pthread_mutex_lock(), pthread_mutex_unlock()

/****************************************************************************/

#define MAX_SAFE_STACK (8 * 1024) /** The maximum stack size which is
                                    guranteed safe to access without faulting.
                                   */

#define NSEC_PER_SEC (1000000000)
#define USEC_PER_SEC (1000000)
#define DIFF_NS(A, B) (((long long) (B).tv_sec - (A).tv_sec) * NSEC_PER_SEC \
        + (B).tv_nsec - (A).tv_nsec)

/****************************************************************************/

#define XNAME(x,y)  x##y
#define NAME(x,y)   XNAME(x,y)

int NAME(MODEL,_init)(void);
int NAME(MODEL,_isr)(double);
int NAME(MODEL,_end)(void);
double NAME(MODEL,_get_tsamp)(void);

/****************************************************************************/

struct pdserv* pdserv;
struct pdtask* pdtask;
static double T = 0.0;
static double Tsamp;

/* Command-line option variables.  */

int priority = -1;      /**< Task priority, -1 means RT (maximum). */
int daemonize = 0;      /**< Become a daemon. */
unsigned int duration_ns = 0;
const char *config = 0;

/***************************************************************************
 * Support functions
 ***************************************************************************/

/** Increment the time.
 * Arguments:
 *  - t: timespec pointer
 *  - dt_ns: increment in nanoseconds
 */
struct timespec* timer_add(struct timespec *t, unsigned int dt_ns)
{
    t->tv_nsec += dt_ns;
    while (t->tv_nsec >= NSEC_PER_SEC) {
        t->tv_nsec -= NSEC_PER_SEC;
        t->tv_sec++;
    }
    return t;
}

/** Return the current system time.
 *
 * This is a callback needed by pdserv.
 */
int gettime(struct timespec *time)
{
    return clock_gettime(CLOCK_REALTIME, time);
}

static inline double calcdiff(struct timespec t1, struct timespec t2)
{
  long diff;
  diff = USEC_PER_SEC * ((long) t1.tv_sec - (long) t2.tv_sec);
  diff += ((int) t1.tv_nsec - (int) t2.tv_nsec) / 1000;
  return (1e-6*diff);
}

double get_run_time(void)
{
  return(T);
}

double get_Tsamp(void)
{
  return(Tsamp);
}

/** Cause a stack fault before entering cyclic operation.
 */
void stack_prefault(void)
{
    unsigned char dummy[MAX_SAFE_STACK];

    memset(dummy, 0, MAX_SAFE_STACK);
}

/** Output the usage.
 */
void usage(FILE *f, const char *base_name)
{
    fprintf(f,
            "Usage: %s [OPTIONS]\n"
            "Options:\n"
            "  --duration       -d secs    Set duration <float>\n"
            "  --config         -c conffile Set configuration file\n"
            "  --priority       -p <PRIO>  Set task priority. Default: RT.\n"
            "  --help           -h         Show this help.\n",
            base_name);
}

/** Get the command-line options.
 */
void get_options(int argc, char **argv)
{
    int c, arg_count;

    static struct option longOptions[] = {
        //name,           has_arg,           flag, val
        {"duration",      required_argument, NULL, 'd'},
        {"config",        required_argument, NULL, 'c'},
        {"priority",      required_argument, NULL, 'p'},
        {"help",          no_argument,       NULL, 'h'},
        {NULL,            no_argument,       NULL,   0}
    };

    do {
        c = getopt_long(argc, argv, "d:c:p:h", longOptions, NULL);

        switch (c) {
            case 'p':
                if (!strcmp(optarg, "RT")) {
                    priority = -1;
                } else {
                    char *end;
                    priority = strtoul(optarg, &end, 10);
                    if (!*optarg || *end) {
                        fprintf(stderr, "Invalid priority: %s\n", optarg);
                        exit(1);
                    }
                }
                break;

            case 'd':
                duration_ns = atof(optarg) * NSEC_PER_SEC;
                break;

            case 'c':
                config = optarg;
                break;

            case 'h':
                usage(stdout, argv[0]);
                exit(0);

            case '?':
                usage(stderr, argv[0]);
                exit(1);

            default:
                break;
        }
    }
    while (c != -1);

    arg_count = argc - optind;

    if (arg_count) {
        fprintf(stderr, "%s takes no arguments!\n", argv[0]);
        usage(stderr, argv[0]);
        exit(1);
    }
}



/****************************************************************************
 * Main function 
 ****************************************************************************/
int main(int argc, char **argv)
{
    unsigned int tsample_ns = (uint64_t)(0.01e9);   // 10ms
    const char* err = NULL;
    int running = 1;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    double exec_time, cycle_time;
    unsigned int overruns = 0;
    struct timespec monotonic_time, world_time;
    struct timespec start_time, stop_time = {0,0}, end_time, last_start_time;
    struct timespec t_current, T0;
 
    get_options(argc, argv);

    Tsamp = NAME(MODEL,_get_tsamp)();

    /////////////////////// setup pdserv //////////////////////////////

    /* Create a pdserv instance */
    if (!(pdserv = pdserv_create("PdServ Test", "1.234", gettime))) {
        err = "Failed to init pdserv.";
        goto out;
    }

    if (config)
        pdserv_config_file(pdserv, config);

    /* Create a task */
    if (!(pdtask = pdserv_create_task(pdserv, Tsamp, NULL))) {
        err = "Failed to create task.";
        goto out;
    }

 
    NAME(MODEL,_init)();

    int ret = pdserv_prepare(pdserv);
    if (ret) {
        err = "Failed to prepare pdserv.";
        goto out;
    }

    /* Lock all memory forever - prevents it from being swapped out. */
    if (mlockall(MCL_CURRENT | MCL_FUTURE))
        fprintf(stderr, "mlockall() failed: %s\n", strerror(errno));

    /* Provoke the first stack fault before cyclic operation. */
    stack_prefault();

    /* Set task priority and scheduler. */
    {
        struct sched_param param = {
            .sched_priority = (priority == -1
                    ? sched_get_priority_max(SCHED_FIFO)
                    : priority),
        };

        if (sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
            fprintf(stderr,
                    "Setting SCHED_FIFO with priority %i failed: %s\n",
                    param.sched_priority, strerror(errno));

            /* Reset priority, so that sub-threads start */
            priority = -1;
        }
    }

    ///////////////////// cyclic task //////////////////////////////////

    clock_gettime(CLOCK_MONOTONIC, &monotonic_time);
    last_start_time = monotonic_time;
    if (duration_ns) {
        stop_time = last_start_time;
        timer_add(&stop_time, duration_ns);
    }

    clock_gettime(CLOCK_MONOTONIC,&T0);

    while (running && (!duration_ns || DIFF_NS(last_start_time, stop_time) > 0)) {
        clock_gettime(CLOCK_MONOTONIC, &start_time);
        clock_gettime(CLOCK_REALTIME, &world_time);

        /* Get a read lock on parameters and a write lock on signals */
        pthread_mutex_lock(&mutex);

        clock_gettime(CLOCK_MONOTONIC,&t_current);

        T = calcdiff(t_current,T0);

        NAME(MODEL,_isr)(T);

        /* Release locks */
        pthread_mutex_unlock(&mutex);

        /* Call at end of calculation task, so that pdserv updates itself */
        pdserv_update(pdtask, &world_time);

        /* Calculate timing statistics */
        cycle_time = 1.0e-9 * DIFF_NS(last_start_time, start_time);
        exec_time  = 1.0e-9 * DIFF_NS(last_start_time, end_time);
        last_start_time = start_time;
        pdserv_update_statistics(pdtask, exec_time, cycle_time, overruns);

        timer_add(&monotonic_time, tsample_ns);  // Increment timer

        clock_gettime(CLOCK_MONOTONIC, &end_time);

        overruns += DIFF_NS(monotonic_time, end_time) > 0;

        /* Wait for next cycle */
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &monotonic_time, 0);
    }

    ///////////////////// clean up /////////////////////////////////////

    NAME(MODEL,_end)();

    /* Clean up */
    pdserv_exit(pdserv);

    pthread_mutex_destroy(&mutex);

out:
    if (err) {
        fprintf(stderr, "Fatal error: %s\n", err);
        return 1;
    }
    return 0;
}

/****************************************************************************/
