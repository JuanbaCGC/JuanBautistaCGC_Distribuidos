install:
	pip install -e .
	sudo apt install zeroc-ice-utils
	sudo apt-get install libzeroc-icestorm3.7 zeroc-icebox

icestorm:
	./run_icestorm

run-test:
	cd tests && \
	./test.sh && \
	cd ..

client:
	./run_client

clean:
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy Announcements"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy UserUpdates"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy CatalogUpdates"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy FileAvailabilityAnnounces"

all-client: install client
