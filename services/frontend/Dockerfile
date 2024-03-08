FROM node:lts-alpine

LABEL version=0.1.0

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

#RUN npm install @vue/cli@5.0.8 -g

COPY package.json .
COPY package-lock.json .
RUN npm install

CMD ["npm", "run", "dev"]