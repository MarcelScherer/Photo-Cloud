clear

# add Server-Script
echo "add Server-Script ..."
sudo mkdir /home/pi/photo_cloud
sudo cp PhotoServerPy.py /home/pi/photo_cloud/
sudo cp PhotoRecPy.py /home/pi/photo_cloud/
sudo cp uninstall_Server.sh /home/pi/photo_cloud/
sudo cp photo_cloud_start /home/pi/photo_cloud/

# add Server-Script to autostart
echo "change directory ..."
cd /home/pi/photo_cloud/
echo "add save foulder ..."
sudo mkdir save
echo "add Server-Script to autostart..."
sudo cp photo_cloud_start /etc/init.d/
sudo chmod +x /etc/init.d/photo_cloud_start
sudo update-rc.d photo_cloud_start defaults

echo "reboot ..."
sudo reboot
