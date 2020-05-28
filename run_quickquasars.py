import numpy as np
import os
import shutil
import glob as glob

def get_slurm_script(script_name,command,outdir,idir,mail,log,part,nodes,threads,time,job_name):
    if os.path.isdir(outdir+'/run') == False:
            os.mkdir(outdir+'/run')
    file_name = outdir + '/run/' +  script_name
    f = open(file_name,'w')
    slurm_dict = dict()
    slurm_dict['line_0'] = '#SBATCH -C haswell\n'
    slurm_dict['line_1'] = '#SBATCH --partition='+part+'\n'
    slurm_dict['line_2'] = '#SBATCH --account=desi\n'
    slurm_dict['line_3'] = '#SBATCH --nodes='+str(nodes)+'\n'
    slurm_dict['line_4'] = '#SBATCH --time='+time+'\n'
    slurm_dict['line_5'] = '#SBATCH --job-name='+job_name+'\n'
    slurm_dict['line_6'] = '#SBATCH --output='+log+'\n'
    slurm_dict['line_7'] = '#SBATCH --mail-user='+mail+'\n'
    slurm_dict['line_8'] = 'idir='+idir+'\n'
    slurm_dict['line_9'] = 'outdir='+outdir+'\n'
    slurm_dict['line_10'] = 'nodes='+str(nodes)+'\n' # CHECK MATCHING #SBATCH --nodes ABOVE !!!!
    slurm_dict['line_11'] = 'nthreads='+str(threads)+'\n' # TO BE TUNED ; CAN HIT NODE MEMORY LIMIT ; 4 is max on edison for nside=16 and ~50 QSOs/deg2
    slurm_dict['line_12'] = 'echo "get list of skewers to run ..."\n'
    slurm_dict['line_13'] = 'files=`\ls -1 $idir/*/*/transmission*.fits*`\n'
    slurm_dict['line_14'] = 'nfiles=`echo $files | wc -w`\n'
    slurm_dict['line_15'] = 'nfilespernode=$((nfiles/nodes+1))\n'
    slurm_dict['line_16'] = 'echo "n files =" $nfiles\n'
    slurm_dict['line_17'] = 'echo "n files per node =" $nfilespernode\n'
    slurm_dict['line_18'] = 'first=1\n'
    slurm_dict['line_19'] = 'last=$nfilespernode\n'
    slurm_dict['line_20'] = 'for node in `seq $nodes` ; do\n'
    slurm_dict['line_21'] = '    echo "starting node $node"\n'
    slurm_dict['line_22'] = '    # list of files to run\n'
    slurm_dict['line_23'] = '    if (( $node == $nodes )) ; then\n'
    slurm_dict['line_24'] = '        last=""\n'
    slurm_dict['line_25'] = '    fi\n'
    slurm_dict['line_26'] = '    echo ${first}-${last}\n'
    slurm_dict['line_27'] = '    tfiles=`echo $files | cut -d " " -f ${first}-${last}`\n'
    slurm_dict['line_28'] = '    first=$(( first + nfilespernode ))\n'
    slurm_dict['line_29'] = '    last=$(( last + nfilespernode ))\n'
    
    set_up = "    srun -N 1 -n 1 -c $nthreads quickquasars -i $tfiles --nproc $nthreads --outdir $outdir/spectra-16 "
    slurm_dict['line_30'] = set_up + command +'\n'
    slurm_dict['line_31'] = '  done\n'
    slurm_dict['line_32'] = 'wait\n'
    slurm_dict['line_33'] = 'echo "END"\n'
    for i in range(len(slurm_dict)):
        f.write(slurm_dict['line_' + str(i)])
    return None

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir',type=str,help='output directory of the quickquasar run')
    parser.add_argument('--idir',type=str,help='directory from where to fetch the input data')
    parser.add_argument('--mail',type=str,default=' ',help='email to sent status of the job')
    parser.add_argument('--log',type=str,default =' ',help='directory to output the log of the job run')
    parser.add_argument('--qos',type=str,default='regular',help='which queue')
    parser.add_argument('--nodes',type=int,default=40,help='number numbers to use')
    parser.add_argument('--threads',type=int,default=4,help='number of thread to use per node')
    parser.add_argument('--time',default='00:30:00',type=str)
    parser.add_argument('--name',type=str,default='lyasim',help='name of the job')
    parser.add_argument('--seed-generator',type=int,default=15430289,help='seed to run quickquasar')
    parser.add_argument('--nruns',type=int,default=1,help='number of quickquasar runs with the same arguments')
    args = parser.parse_args()

    outfile = open('submit.sh','w+')
    np.random.seed(args.seed_generator)
    for k in range(args.nruns):
        #make the output dirs
        output_dirs = args.outdir + '_'+str(k)
        if os.path.isdir(output_dirs) == False:
            os.mkdir(output_dirs)
        if os.path.isdir(output_dirs+'/logs') == False:
            os.mkdir(output_dirs+'/logs')
        if os.path.isdir(output_dirs+'/spectra-16') == False:
            os.mkdir(output_dirs+'/spectra-16')
        
        
        seed = np.random.randint(12345,98765,size=1)

        #read config file for quickquasart
        file = open('config.txt','r')
        lines = []
        for l in file:
            lines.append(l)
        
        for i in range(len(lines)):
            line_comp = lines[i].split()
            if len(line_comp) != 1:
                lines[i] = '--' + line_comp[0] + ' ' + line_comp[1] + ' ' 
            else:
                lines[i] = '--' + line_comp[0] + ' '
        
        command =  "".join(lines) + '--seed '+str(seed[0]) 

        name = 'run_quickquasar.sh'
        get_slurm_script(name,command,output_dirs,args.idir,args.mail,args.log,args.qos,args.nodes,args.threads,args.time,args.name) 
        
        
        outfile.write('sbatch '+output_dirs+'/run/'+name+'\n')
    outfile.close()
