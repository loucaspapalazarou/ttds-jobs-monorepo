# Jobs Search Engine

*Repository for the final assignment of* ***Text Technologies for Data Science*** *at The University of Edinburgh*

---

See the [final report]() (**TODO**: add link to report or embed pdf)

The entire codebase for the project is structured as a monolith in this repository. We implemented 3 distinct services.

- `frontend`
- `backend`
- `data-colection`

All the services are placed in the `services` directory, each with their own documentation.

Start the system:
```
sudo docker-compose up -d --build
```

Under normal circumstances, data collection will run once a day. If there is a need to start a data-collection task right away, use:
```
sudo docker-compose -f docker-compose-data-collection.yml up -d --build
```