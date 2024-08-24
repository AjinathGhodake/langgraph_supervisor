import requests
import os
import zipfile
import io


def create_spring_boot_app(
    group_id, artifact_id, dependencies, type, language, boot_version, base_dir
):
    """
    Generates a Spring Boot application using Spring Initializr and extracts it to the specified directory.

    Args:
        group_id (str): The group ID of the project (e.g., 'com.example').
        artifact_id (str): The artifact ID of the project (e.g., 'myapp').
        dependencies (str): A comma-separated list of dependencies to include (e.g., 'web').
        type (str): The type of project (e.g., 'maven-project' or 'gradle-project').
        language (str): The programming language (e.g., 'java').
        boot_version (str): The version of Spring Boot to use (e.g., '2.7.3').
        base_dir (str): The directory where the project should be generated.

    Returns:
        str: The path to the generated Spring Boot project.
    """

    # Construct the URL for Spring Initializr
    spring_initializr_url = "https://start.spring.io/starter.zip?type=gradle-project&language=java&bootVersion=3.3.3&baseDir=demo&groupId=com.example&artifactId=demo&name=demo&description=Demo%20project%20for%20Spring%20Boot&packageName=com.example.demo&packaging=jar&javaVersion=17"

    print(f"Generated URL: {spring_initializr_url}")  # For debugging

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


# Example usage
if __name__ == "__main__":
    project_path = create_spring_boot_app(
        group_id="com.example",
        artifact_id="myapp",
        dependencies="web",  # Single dependency for testing
        type="maven-project",
        language="java",
        boot_version="2.6.9",  # Make sure this is valid
        base_dir="./generated_spring_app",
    )
    print(f"Project created at: {project_path}")
