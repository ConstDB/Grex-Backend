docker compose down -v
sudo rm -rf ./data/
sudo mkdir -p ./data/pgadmin-data
sudo chown -R 5050:5050 ./data/pgadmin-data
docker compose up