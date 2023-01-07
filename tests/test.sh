#!/bin/bash
echo "Se va a anunciar el Main en el topic Announcements..."
./main_test.py
sleep 5

echo "Se va a anunciar un Catálogo en el topic Announcements & CatalogUpdates..."
./catalog_test.py
sleep 3

echo "Se van a hacer actualizaciones en Authenticator por el topic UserUpdates..."
./authenticator_test.py
sleep 3

echo "Mediante el topic FileAvailabilityAnnounces se van a comunicar los ids de los archivos disponibles en un FileService..."
./fileService_test.py