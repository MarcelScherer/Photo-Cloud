clear

# add Server-Script
echo "*** uninstall Server-Script ***"
echo " "
sudo update-rc.d -f  /etc/init.d/photo_cloud_start remove
echo "stop autostart ...."
sudo rm /etc/init.d/photo_cloud_start
echo "deleate autostart script ...."
sudo rm -r /home/pi/photo_cloud/
echo "deleate photo cloud foulder ...."

echo "reboot ..."
sudo reboot
