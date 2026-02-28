from features.interview.domain.enums import Level

MAX_QUESTIONS = 5

LEVELS: list[Level] = list(Level)

ROLES: dict[str, dict[str, list[str]]] = {
    "프론트엔드": {
        "frameworks": ["React", "Vue", "Angular", "Next.js", "Svelte"],
        "extras": ["TypeScript", "Tailwind CSS", "GraphQL", "Webpack/Vite", "Testing (Jest/RTL)"],
    },
    "백엔드": {
        "frameworks": ["Spring Boot", "FastAPI", "Django", "Node.js/Express", "NestJS", "Go/Gin", "Laravel"],
        "extras": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "GraphQL", "gRPC", "Kafka", "ElasticSearch"],
    },
    "풀스택": {
        "frameworks": ["Next.js", "Nuxt.js", "SvelteKit", "Django + React", "Rails + React"],
        "extras": ["TypeScript", "PostgreSQL", "Redis", "Docker", "GraphQL"],
    },
    "데이터 분석": {
        "frameworks": ["Python/Pandas", "SQL", "R"],
        "extras": ["Tableau", "Power BI", "Spark", "Scikit-learn", "A/B Testing"],
    },
    "데이터 엔지니어": {
        "frameworks": ["Apache Spark", "Apache Kafka", "Apache Airflow"],
        "extras": ["dbt", "Flink", "Snowflake", "BigQuery", "Databricks", "Hadoop"],
    },
    "ML/AI 엔지니어": {
        "frameworks": ["PyTorch", "TensorFlow", "Scikit-learn"],
        "extras": ["MLflow", "Hugging Face", "LangChain", "Kubernetes", "FastAPI", "CUDA"],
    },
    "DevOps": {
        "frameworks": ["Docker/Kubernetes", "GitHub Actions", "Jenkins"],
        "extras": ["AWS", "GCP", "Azure", "Terraform", "ArgoCD", "Prometheus/Grafana", "Ansible"],
    },
    "클라우드 엔지니어": {
        "frameworks": ["AWS", "GCP", "Azure"],
        "extras": ["Terraform", "Kubernetes", "Pulumi", "CDK", "Serverless", "비용 최적화"],
    },
    "모바일": {
        "frameworks": ["React Native", "Flutter", "Swift (iOS)", "Kotlin (Android)"],
        "extras": ["Firebase", "GraphQL", "REST API", "CI/CD (Fastlane)", "앱스토어 배포"],
    },
}

