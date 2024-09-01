from langchain_core.tools import tool
import requests
import os
import zipfile
import io
import shutil
import subprocess
import stat
import logging
import signal


from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(max_results=5)
logging.basicConfig(level=logging.INFO, filename="execution.log", filemode="w")


@tool
def initialize_spring_boot_app(
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
    Initialize a Spring Boot application using Spring Initializer and extracts it to the specified directory.
    When start the initialization clear the ./generated_spring_app directory

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
        boot_version (str): The version of Spring Boot to use (e.g., '3.3.3').
        packaging(str): the type of packaging (e.g., war,jar)
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
            boot_version='3.3.3',
            packaging='war'
            base_dir='./generated_spring_app'
        )
        print(f"Project created at: {project_path}")
    """
    # Construct the URL for Spring Initializr
    spring_initialize_url = (
        f"https://start.spring.io/starter.zip?type={type}&language={language}&bootVersion={boot_version}"
        f"&baseDir={artifact_id}&groupId={group_id}&artifactId={artifact_id}&name={name}"
        f"&description={description}&packageName={package_name}&packaging={packaging}"
        f"&javaVersion={java_version}&dependencies={dependencies}"
    )

    try:
        # Send GET request to Spring Initializr to download the project zip
        response = requests.get(spring_initialize_url)
        response.raise_for_status()

        # Overwrite the directory
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)  # Delete the existing directory
            print(f"Deleted existing directory: {base_dir}")

        os.makedirs(base_dir)  # Create a new directory with the same name
        print(f"Created new directory: {base_dir}")

        # Unzip the downloaded project archive into the base directory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(base_dir)

        project_path = os.path.join(base_dir, artifact_id)
        print(f"Spring Boot application generated at: {project_path}")
        return project_path

    except requests.exceptions.RequestException as e:
        print(f"Error generating Spring Boot application: {e}")
        raise


@tool
def spring_boot_code_exists_test(project_path="./generated_spring_app/myapp"):
    """
    Run basic tests on the initialized Spring Boot application to ensure it was generated correctly.

    Args:
        project_path (str): The path to the generated Spring Boot project.

    Returns:
        dict: A dictionary containing the results of the tests (e.g., whether the application starts up, key files exist).

    Example:
        test_results = spring_boot_code_exists_test(project_path='./generated_spring_app/myapp')
        print(test_results)
    """

    test_results = {
        "project_exists": False,
        "mvnw_exists": False,
        "pom_exists": False,
        "app_starts": False,
    }
    project_path = "./generated_spring_app/myapp"
    print(">>>>>>project_path", project_path)

    # Check if the project directory exists
    if os.path.exists(project_path):
        test_results["project_exists"] = True

        # Check for Maven wrapper script
        mvnw_path = os.path.join(project_path, "mvnw")
        if os.path.exists(mvnw_path):
            test_results["mvnw_exists"] = True

            # Ensure the mvnw script has executable permissions
            st = os.stat(mvnw_path)
            os.chmod(mvnw_path, st.st_mode | stat.S_IEXEC)

        # Check for pom.xml file
        pom_path = os.path.join(project_path, "pom.xml")
        if os.path.exists(pom_path):
            test_results["pom_exists"] = True

        # Try to start the Spring Boot application
        try:
            process = subprocess.Popen(
                ["./mvnw", "spring-boot:run"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Ensures the output is in text format
            )

            # Monitor the output for successful start
            for stdout_line in iter(process.stdout.readline, ""):
                logging.info(stdout_line.strip())
                print(stdout_line.strip())
                if "Started MyAppApplication" in stdout_line:
                    test_results["app_starts"] = True
                    break

            # Terminate the application gracefully if it started
            if test_results["app_starts"]:
                process.send_signal(
                    signal.SIGINT
                )  # Send SIGINT to stop the application

            # Wait for the process to terminate
            process.stdout.close()
            process.stderr.close()
            process.wait()

        except subprocess.CalledProcessError as e:
            print(f"Error starting Spring Boot application: {e}")
            test_results["app_starts"] = False

        print("Status of testing:", test_results)
    else:
        print(f"Project directory {project_path} does not exist.")

    return test_results
