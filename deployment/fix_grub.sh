#!/bin/bash
# Script to force HDMI resolution on AMD GPU
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash video=HDMI-A-1:1920x1080@60e"/' /etc/default/grub
update-grub
reboot
