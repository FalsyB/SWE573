#!/bin/bash
################################################################################
# @file build.sh
# @author Cetin Mericli <cetin@atlas-robotics.com>
# @brief Build Atlas base Docker image
# @date 2018-10-22
#
# @copyright
# Copyright (c) 2018 Atlas Robotics\n
# All Rights Reserved.\n
# CONFIDENTIAL and PROPRIETARY\n
# @par
#
# @internal
# @par History
# * 2018-10-22 Cetin Mericli <cetin@atlas-robotics.com> created file.
################################################################################
FROM=${1:-18.04}

docker build --build-arg from=ubuntu:$FROM -t burakproject/base:$FROM .
