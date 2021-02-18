sudo -u postgres createuser hosteluser -s
sudo -u postgres createdb hosteluser


echo "HOSTEL\n\n\n\n\n\n" | adduser hosteluser --quite --disabled-password

./reset.expect hosteluser "admin123"

sudo -u postgres psql -c "ALTER USER hosteluser PASSWORD 'admin123';"

sudo -u postgres psql -c "create database hostelmanagement;"
