# Reference multi-stage Dockerfile for a Spring Boot service.
# Conventions explained in ai/skills/deployment/references/docker.md — copy into a service and adjust ARGs.

# ---------- Build stage ----------
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# Dependency layer first: cache survives source-only changes
COPY pom.xml .
RUN mvn -q -B dependency:go-offline

COPY src ./src
RUN mvn -q -B package -DskipTests

# Extract Spring Boot layered jar for better runtime layer caching
RUN java -Djarmode=layertools -jar target/*.jar extract --destination extracted

# ---------- Runtime stage ----------
FROM eclipse-temurin:21-jre-jammy AS runtime

# Non-root, always
RUN groupadd --system app && useradd --system --gid app app
USER app
WORKDIR /app

COPY --from=build /workspace/extracted/dependencies/ ./
COPY --from=build /workspace/extracted/spring-boot-loader/ ./
COPY --from=build /workspace/extracted/snapshot-dependencies/ ./
COPY --from=build /workspace/extracted/application/ ./

# Respect container memory limits; leave per-env tuning to JAVA_OPTS
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"

EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
