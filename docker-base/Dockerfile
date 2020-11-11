################################################################################
# @file Dockerfile
# @author Burak Eruçar <burak.erucar@boun.edu.tr>
# @brief SWE573 base Docker image
# @date 2020-11-03
#
# @copyright
# Copyright (c) 2020 Bogazici University\n
# All Rights Reserved.\n
# CONFIDENTIAL and PROPRIETARY\n
# @par
#
# @internal
# @par History
################################################################################
ARG from=ubuntu:18.04

FROM ${from}

LABEL maintainer="Burak Eruçar burak.erucar@boun.edu.tr" 

RUN apt-key adv --keyserver keys.gnupg.net --recv-key C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key C8B3A55A6F3EFCDE
RUN apt-get update && apt-get install -y --no-install-recommends \
# very basic tools
        sudo \
        lsb-release \ 
        gnupg \
        locales \
        mlocate \
        git \
        ssh \
        usbutils \
        htop \
        apt-utils \
	binutils \
        iputils-ping \
	apt-transport-https \
	net-tools \
	build-essential \
        linux-tools-common \
        google-perftools \
        iperf \
        locate \
        gdb \
       	bash-completion \
	software-properties-common \
	ipython \
       	screen \
	nano \
# OpenGL related        
        libxau6 \
        libxdmcp6 \
        libxcb1 \
        libxext6 \
        libx11-6 && \
    rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8    

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
        ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
        ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics,compat32,utility

# Required for non-glvnd setups.
ENV LD_LIBRARY_PATH /usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

# Atlas user
ARG CUSTOM_USER=atlas 
ARG CUSTOM_UID=1000
ENV CUSTOM_UID ${CUSTOM_UID}
ENV CUSTOM_USER ${CUSTOM_USER}
RUN adduser -u $CUSTOM_UID --disabled-password --gecos '' $CUSTOM_USER \
 && adduser $CUSTOM_USER sudo \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
ENV HOME /home/$CUSTOM_USER

WORKDIR ${HOME}

# Add the ssh key for automated jobs
ADD --chown=atlas:atlas atlas_cicd_key* ${HOME}/.ssh/
RUN echo "    IdentityFile ~/.ssh/atlas_cicd_key" >> /etc/ssh/ssh_config \
    && chmod 400 ${HOME}/.ssh/atlas_cicd_key \
    && ssh-keyscan -t rsa,dsa bitbucket.org 2>&1 > ~/.ssh/known_hosts

# For CAN and video camera access
RUN usermod -a -G dialout $CUSTOM_USER
RUN usermod -a -G video $CUSTOM_USER

# Forgot what this was for. Will uncomment if still needed
#RUN cp -f /var/lib/dbus/machine-id /etc/machine-id

USER $CUSTOM_USER

# Let there be color (in the terminal)
RUN sed -i -- 's/#force_color_prompt=yes/force_color_prompt=yes/g' ~/.bashrc
