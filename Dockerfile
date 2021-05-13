FROM openjdk:11
COPY . /usr/src/ner4soft
WORKDIR /usr/src/ner4soft/valkyr-ie
EXPOSE 8080
CMD ["java", "-jar", "valkyr-ie-gate-1.0.jar"]
