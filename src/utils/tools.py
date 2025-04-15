from langchain_core.tools import tool
import requests
import os
import zipfile
import io
import subprocess
import stat
import logging
import signal


from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(max_results=5)
logging.basicConfig(level=logging.INFO, filename="execution.log", filemode="w")


@tool
def initialize_spring_boot_app(
    group_id: str,
    artifact_id: str,
    name: str,
    description: str,
    package_name: str,
    dependencies: str,
    java_version: str,
    type: str,
    language: str,
    boot_version: str,
    packaging: str,
    base_dir: str,
) -> str:
    """
    Initializes a Spring Boot application using Spring Initializer.
    Returns:
        The path to the generated Spring Boot project.

    Raises:
        requests.exceptions.RequestException: If the request to Spring Initializr fails.

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
    try:
        # Use absolute path for the directory
        absolute_base_dir = os.path.abspath(base_dir)
        directory_exists = os.path.exists(absolute_base_dir)

        if directory_exists:
            project_path = os.path.join(absolute_base_dir, artifact_id)
            return {
                "next": "supervisor",
                "project_path": project_path,
                "key_files": [os.path.join(project_path, "pom.xml")],
            }
        else:
            spring_initialize_url = (
                f"https://start.spring.io/starter.zip?type={type}&language={language}&bootVersion={boot_version}"
                f"&baseDir={artifact_id}&groupId={group_id}&artifactId={artifact_id}&name={name}"
                f"&description={description}&packageName={package_name}&packaging={packaging}"
                f"&javaVersion={java_version}&dependencies={dependencies}"
            )
            response = requests.get(spring_initialize_url)
            response.raise_for_status()

            if not os.path.exists(absolute_base_dir):
                os.makedirs(absolute_base_dir)

            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(absolute_base_dir)

            project_path = os.path.join(absolute_base_dir, artifact_id)
            print(f"Spring Boot application generated at: {project_path}")
            return project_path

    except requests.exceptions.RequestException as e:
        print(f"Error generating Spring Boot application: {e}")
        raise


@tool
def spring_boot_code_exists_test(project_path=None):
    """
    Run basic tests on the initialized Spring Boot application to ensure it was generated correctly.

    Args:
        project_path (str): The path to the generated Spring Boot project.

    Returns:
        dict: A dictionary containing the results of the tests (e.g., whether the application starts up,
              key files exist).

    Example:
        test_results = spring_boot_code_exists_test(
            project_path='./generated_spring_app/myapp'
        )
        print(test_results)
    """

    test_results = {
        "project_exists": False,
        "mvnw_exists": False,
        "pom_exists": False,
        "app_starts": False,
    }

    # If no project_path is provided, use default but make it an absolute path
    if project_path is None:
        default_path = "./generate_spring_app/myapp"
        project_path = os.path.abspath(default_path)
    else:
        project_path = os.path.abspath(project_path)

    print(f"Testing Spring Boot application at: {project_path}")

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


@tool
def read_file_content(file_path: str):
    """
    Read the content of a file from the given path.

    Args:
        file_path (str): The path of the file to read.

    Returns:
        str: The content of the file as a string.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        IOError: If an I/O error occurs while reading the file.
    """
    try:
        # Convert to absolute path if not already
        abs_file_path = os.path.abspath(file_path)
        with open(abs_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {abs_file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {abs_file_path}: {e}")


@tool
def write_controller_code(file_path: str, java_code: str):
    """
    Write the given Java controller code to the specified file.

    Args:
        file_path (str): The path where the Java controller file should be created.
        java_code (str): The Java controller code to be written to the file.

    Returns:
        str: A message indicating the success of the operation.

    Example:
        write_controller_code(
            file_path='./generated_spring_app/myapp/src/main/java/com/example/myapp/controller/MyController.java',
            java_code='public class MyController { ... }'
        )
    """
    # Convert to absolute path and ensure the directory exists
    abs_file_path = os.path.abspath(file_path)
    directory = os.path.dirname(abs_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the Java code to the file
    with open(abs_file_path, "w") as file:
        file.write(java_code)

    return f"Java controller code has been written to {abs_file_path}"


@tool()
def default_tool():
    """Default tool"""
    pass
