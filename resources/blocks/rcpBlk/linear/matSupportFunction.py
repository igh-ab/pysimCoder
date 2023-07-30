
def addMatMult(mdlflags,data):
        if 'matmult' in data:
            return
        data['matmult']="""
        int matmult(double *a, int na, int ma, double *b, int nb, int mb, double* c)
        {
            int i, j, k;

            if (ma!=nb){
                // fprintf(stderr,"MATMULT: A and B matrices: Incompatible sizes");
                return -1;
            }

            for(i=0;i<na;i++){
                for(j=0;j<mb;j++){
                c[i*mb+j] = 0;
                for(k=0;k<ma;k++)
                c[i*mb+j] += a[i*ma+k]*b[k*mb+j];
                }
            }
            return 0;
        }
        """

def addMatSum(mdlflags,data):
        if 'matsum' in data:
            return
        data['matsum']="""
        int matsum(double *a, int na, int ma, double *b, int nb, int mb, double* c)
        {
            int i;

            if ((na != nb) || (ma != mb)){
                // fprintf(stderr,"MATSUM: A and B matrices: Incompatible sizes");
                return -1;
            }

            for(i=0; i<na*ma; i++) c[i] = a[i]+b[i];
            return 0;
        }
        """
