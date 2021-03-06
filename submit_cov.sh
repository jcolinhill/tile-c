#!/bin/bash

mpi_niagara 1 "python bin/make_cov.py v1.2.0 deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06,p01,p02,p03,p04,p05,p06,p07,p08 -o" -t 80 --walltime "01:45:00"
mpi_niagara 1 "python bin/make_cov.py v1.2.0 boss boss_01,boss_02,boss_03,boss_04,p01,p02,p03,p04,p05,p06,p07,p08 --o" -t 80 --walltime "02:00:00"


# mpi_niagara 1 "python bin/make_cov.py v1.1.0 deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06,p01,p02,p03,p04,p05,p06,p07,p08 -o" -t 80 --walltime "01:45:00"
# mpi_niagara 1 "python bin/make_cov.py v1.1.0 boss boss_01,boss_02,boss_03,boss_04,p01,p02,p03,p04,p05,p06,p07,p08 --o" -t 80 --walltime "02:00:00"


#mpi_niagara 1 "python bin/make_cov.py yy_split_0_v1.0.0_rc deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06 -o --split-set 0" -t 80 --walltime "01:45:00"
#mpi_niagara 1 "python bin/make_cov.py yy_split_0_v1.0.0_rc boss boss_01,boss_02,boss_03,boss_04 --o  --split-set 0" -t 80 --walltime "02:00:00"
#mpi_niagara 1 "python bin/make_cov.py yy_split_1_v1.0.0_rc deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06 -o  --split-set 1" -t 80 --walltime "01:45:00"
#mpi_niagara 1 "python bin/make_cov.py yy_split_1_v1.0.0_rc boss boss_01,boss_02,boss_03,boss_04 --o  --split-set 1" -t 80 --walltime "02:00:00"




#mpi_niagara 1 "python bin/make_cov.py v1.0.0_rc deep8 deep8_01,deep8_02,deep8_03,deep8_04,p01,p02,p03,p04,p05,p06,p07,p08 --o" -t 80 --walltime "02:00:00"

# Isotropic
# mpi_niagara 1 "python bin/make_cov.py iso_v1.0.0_rc deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06,p01,p02,p03,p04,p05,p06,p07,p08 -o --isotropic-override" -t 80 --walltime "01:45:00"
# mpi_niagara 1 "python bin/make_cov.py iso_v1.0.0_rc boss boss_01,boss_02,boss_03,boss_04,p01,p02,p03,p04,p05,p06,p07,p08 --o  --isotropic-override" -t 80 --walltime "02:00:00"


# Extra time for fresh inpainting
#mpi_niagara 1 "python bin/make_cov.py v1.0.0_rc deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06,p01,p02,p03,p04,p05,p06,p07,p08 -o" -t 80 --walltime "02:45:00"
#mpi_niagara 1 "python bin/make_cov.py v1.0.0_rc boss boss_01,boss_02,boss_03,boss_04,p01,p02,p03,p04,p05,p06,p07,p08 --o" -t 80 --walltime "03:00:00"



#mpi_niagara 1 "python bin/make_cov.py test_v1.0.0_rc boss boss_01,boss_02,boss_03,boss_04,p01,p02,p03,p04,p05,p06,p07,p08 --o" -t 80 --walltime "00:30:00"
#mpi_niagara 1 "python bin/make_cov.py test_v1.0.0_rc deep56 d56_01,d56_02,d56_03,d56_04,d56_05,d56_06,p01,p02,p03,p04,p05,p06,p07,p08 -o" -t 80 --walltime "00:15:00"
