# Makefile for source rpm: cups
# $Id$
NAME := cups
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
