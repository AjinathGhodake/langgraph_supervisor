from langchain_core.tools import tool
import requests
import os
import zipfile
import io

# from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def create_spring_boot_app(
    group_id,
    artifact_id,
    name,
    description,
    package_name,
    dependencies,
    java_version,
    type,
    language,
    boot_version,
    packaging,
    base_dir,
):
    """
    Generates a Spring Boot application using Spring Initializr and extracts it to the specified directory.

    Args:
        group_id (str): The group ID of the project (e.g., 'com.example').
        artifact_id (str): The artifact ID of the project (e.g., 'myapp').
        name (str): The name of the project (e.g., 'MyApp').
        description (str): A brief description of the project.
        package_name (str): The base package name for the project (e.g., 'com.example.myapp').
        dependencies (str): A comma-separated list of dependencies to include (e.g., 'web,data-jpa,h2').
        java_version (str): The version of Java to use (e.g., '17').
        type (str): The type of project (e.g., 'maven-project' or 'gradle-project').
        language (str): The programming language (e.g., 'java').
        boot_version (str): The version of Spring Boot to use (e.g., '3.0.0').
        base_dir (str): The directory where the project should be generated.

    Returns:
        str: The path to the generated Spring Boot project.

    Raises:
        requests.exceptions.RequestException: If the request to Spring Initializr fails.
        zipfile.BadZipFile: If there is an issue with unzipping the downloaded project archive.

    Example:
        project_path = create_spring_boot_app(
            group_id='com.example',
            artifact_id='myapp',
            name='MyApp',
            description='A Spring Boot application',
            package_name='com.example.myapp',
            dependencies='web,data-jpa,h2',
            java_version='17',
            type='maven-project',
            language='java',
            boot_version='3.0.0',
            base_dir='./generated_spring_app'
        )
        print(f"Project created at: {project_path}")
    """
    # Construct the URL for Spring Initializr
    spring_initializr_url = (
        f"https://start.spring.io/starter.zip?type={type}&language={language}&bootVersion={boot_version}"
        f"&baseDir={artifact_id}&groupId={group_id}&artifactId={artifact_id}&name={name}"
        f"&description={description}&packageName={package_name}&packaging={packaging}"
        f"&javaVersion={java_version}&dependencies={dependencies}"
    )

    try:
        # Send GET request to Spring Initializr to download the project zip
        response = requests.get(spring_initializr_url)
        response.raise_for_status()

        # Create the base directory if it doesn't exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Unzip the downloaded project archive into the base directory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(base_dir)

        project_path = os.path.join(base_dir, artifact_id)
        print(f"Spring Boot application generated at: {project_path}")
        return project_path

    except requests.exceptions.RequestException as e:
        print(f"Error generating Spring Boot application: {e}")
        raise


# tools = [TavilySearchResults(max_results=1)]
tools = [multiply, create_spring_boot_app]
