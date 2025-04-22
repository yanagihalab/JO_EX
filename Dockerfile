FROM openjdk:8-jdk-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app

RUN git clone --branch v0.8.0 https://github.com/dsg-titech/simblock.git

WORKDIR /app/simblock

RUN chmod +x ./gradlew && ./gradlew build

RUN mkdir -p /app/simblock/simulator/src/dist/output/graph/

CMD ["./gradlew", ":simulator:run"]
