
# This is just a test command with bubblewrap
#bwrap --unshare-all --tmpfs / --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /media/caioh-linux/EXTERNAL_HDD1/Mestrado/astar_msa/bin/ /msa -- /msa/msa_pastar --help

# Copy everything to the build directory
# Put all of the dependencies at the 'dependencies' folder
# All files shound be at the same directory
cp '/lib/x86_64-linux-gnu/libstdc++.so.6' ./dependencies/;
cp '/lib/x86_64-linux-gnu/libboost_program_options.so.1.74.0' ./dependencies/;
cp '/lib/x86_64-linux-gnu/libboost_filesystem.so.1.74.0' ./dependencies/;
cp '/lib/x86_64-linux-gnu/libm.so.6' ./dependencies/;
cp '/lib/x86_64-linux-gnu/libgcc_s.so.1' ./dependencies/;
cp '/lib/x86_64-linux-gnu/libc.so.6' ./dependencies/;
cp '/lib64/ld-linux-x86-64.so.2' ./dependencies/;

# Get the executable (you may change the path on your machine)
cp '/media/caioh-linux/EXTERNAL_HDD1/Mestrado/astar_msa/bin/msa_pastar' './msa/';
