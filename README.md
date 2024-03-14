# Jobs Search Engine

*Repository for the final assignment of* ***Text Technologies for Data Science*** *at The University of Edinburgh*

---

See the [final report](#) (**TODO:** Link to report or embedded PDF)

The entire codebase for the project is structured as a monolith in this repository. We implemented 3 distinct services:

- `frontend`
- `backend`
- `data-collection`

All the services are placed in the `services/` directory, each with their own documentation. A module for index processing is also present. In addition to the custom services, the system utilizes PostgreSQL for data storage, and Redis as a caching mechanism for the inverted index.

Start the system:
```
sudo docker-compose up -d --build
```

Under normal circumstances, data collection will run once a day. If there is a need to start a data-collection task right away, use:
```
sudo docker-compose -f docker-compose-data-collection.yml up -d --build
```