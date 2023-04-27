
# Build command: podman build -t pastar_container -f msa_pastar_container.dockerfile .
# Do not use any base image (this is to avoid relying on DockerHub for example)
FROM scratch

# You must create a ./dependencies and a ./msa folders at the buid directory since dockerfiles only read relative paths
# Copying all of the dependencies from the host machine (get them with ldd)
COPY /dependencies/libstdc++.so.6 /lib/x86_64-linux-gnu/
COPY /dependencies/libboost_program_options.so.1.74.0 /lib/x86_64-linux-gnu/
COPY /dependencies/libboost_filesystem.so.1.74.0 /lib/x86_64-linux-gnu/
COPY /dependencies/libm.so.6 /lib/x86_64-linux-gnu/
COPY /dependencies/libgcc_s.so.1 /lib/x86_64-linux-gnu/
COPY /dependencies/libc.so.6 /lib/x86_64-linux-gnu/
COPY /dependencies/ld-linux-x86-64.so.2 /lib64/

# Getting the executable
COPY /msa/msa_pastar /msa/

# Setting the executable folder as the workdir for ease of use
WORKDIR /msa

# Treat the container as an executable (you may use CMD if you want)
ENTRYPOINT ["./msa_pastar"]

# How to execute
# ENTRYPOINT: podman run --rm -it pastar_container:latest --help
# CMD: podman run --rm -it pastar_container:latest /msa/msa_pastar --help