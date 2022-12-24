/*
COPYRIGHT (C) 2022  Roberto Bucher (roberto.bucher@supsi.ch)

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <rmw_microros/rmw_microros.h>

#include <microros/pysim_interfaces/msg/pysim_publisher.h>
#include <microros/pysim_interfaces/msg/pysim_subscriber.h>

#include <pyblock.h>
#include <string.h>

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){printf("Failed status on line %d: %d. Aborting.\n",__LINE__,(int)temp_rc); return 1;}}

static int nNodes = 0;
void ** yGlobal;

static void init(python_block *block)
{
  int * intPar    = block->intPar;
  char pub[20];
  char subs[20];
  int n = intPar[0];

  if(nNode){
    printf("Max 1 microROS node allowed!\n");
    exit(1);
  }
  strncpy(pub, block->str,n);
  strcpy(subs, &(block->str[n]));
  pub[n]='\0';
  printf("publisher: %s\n", pub);
  printf("subscriber: %s\n", subs);
  yGlobal = block.y;

  
  
}

static void inout(python_block *block)
{
  /* double *y = block->y[0]; */
  /* double *u = block->u[0]; */
  
}

static void end(python_block *block)
{
  /* double * realPar = block->realPar; */
  /* int * intPar    = block->intPar; */
  /* double *y = block->y[0]; */
  /* double *u = block->u[0]; */

}

void microros(int flag, python_block *block)
{
  if (flag==CG_OUT){          /* get input */
    inout(block);
  }
  else if (flag==CG_END){     /* termination */ 
    end(block);
  }
  else if (flag ==CG_INIT){    /* initialisation */
    init(block);
  }
}


