<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="20%" alt="YT2DOC-logo">
</p>
<p align="center">
    <h1 align="center">YT2DOC</h1>
</p>
<p align="center">
    <em>Whispering insights, crafting structured narratives.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/shun-liang/yt2doc?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/shun-liang/yt2doc?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/shun-liang/yt2doc?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/shun-liang/yt2doc?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

yt2doc simplifies creating structured documents from YouTube videos and playlists, enhancing accessibility and searchability. Ideal for content creators and researchers, it automates transcription and formatting, streamlining the process for generating organized and readable content.

---

##  Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Architecture**  | <ul><li>Utilizes a modular architecture with components like `yt2doc`, `transcription`, `formatting`, and `extraction` for clear separation of concerns.</li><li>Employs interfaces to define contracts between different modules, promoting extensibility and maintainability.</li><li>Implements a file cache system for efficient storage and retrieval of chaptered transcripts, enhancing performance.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Follows PEP 8 guidelines for Python code formatting and style consistency.</li><li>Includes comprehensive unit tests using `pytest` to ensure code correctness and reliability.</li><li>Leverages type hints and annotations for improved code readability and maintainability.</li></ul> |
| 📄 | **Documentation** | <ul><li>Provides detailed documentation in Python format, including `txt`, `lock`, `toml`, and `py` files for clear understanding of project structure and configurations.</li><li>Offers installation and usage commands for easy setup and execution of the project.</li><li>Includes test commands using `pytest` for validating project functionality.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with various external libraries and tools such as `yt-dlp`, `transformers`, and `scikit-learn` for enhanced functionality.</li><li>Utilizes `whisper.cpp` and `FasterWhisper` adapters for language detection and audio transcription.</li><li>Supports integration with different Whisper backends for flexible transcription options.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Divides functionality into separate modules like `transcription`, `formatting`, and `extraction` for cohesive and manageable code organization.</li><li>Defines clear interfaces between modules to facilitate independent development and testing.</li><li>Encourages reusability and scalability through modular design principles.</li></ul> |
| 🧪 | **Testing**       | <ul><li>Implements unit tests using `pytest` to validate the functionality of different components and ensure code reliability.</li><li>Includes test coverage for critical paths and edge cases to maintain robustness.</li><li>Utilizes test-driven development practices to enhance code quality and correctness.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Optimizes performance through efficient caching mechanisms for storing and retrieving chaptered transcripts.</li><li>Utilizes parallel processing and optimized algorithms for faster transcription and formatting of video content.</li><li>Employs lightweight data structures and algorithms to minimize resource consumption and improve overall performance.</li></ul> |

---

##  Project Structure

```sh
└── yt2doc/
    ├── LICENSE
    ├── README.md
    ├── cli
    │   ├── __init__.py
    │   └── main.py
    ├── pyproject.toml
    ├── requirements.txt
    ├── uv.lock
    └── yt2doc
        ├── __init__.py
        ├── extraction
        ├── factories.py
        ├── formatting
        ├── timer.py
        ├── transcription
        ├── writer.py
        ├── youtube
        └── yt2doc.py
```


###  Project Index
<details open>
	<summary><b><code>YT2DOC/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td>Generates project dependencies from a specified configuration file, ensuring accurate package versions for seamless integration within the codebase architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/pyproject.toml'>pyproject.toml</a></b></td>
				<td>Define project dependencies and configurations in pyproject.toml for the yt-extractor project, ensuring compatibility and functionality with specified versions.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- cli Submodule -->
		<summary><b>cli</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/cli/main.py'>main.py</a></b></td>
				<td>- Facilitates video and playlist transcription using different Whisper backends<br>- Determines the appropriate Whisper adapter based on the chosen backend, then generates transcripts and writes them to the specified output location<br>- Handles caching and segmentation options for enhanced document creation.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- yt2doc Submodule -->
		<summary><b>yt2doc</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/timer.py'>timer.py</a></b></td>
				<td>Implements a Timer class to measure elapsed time within the project.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/factories.py'>factories.py</a></b></td>
				<td>- Creates a Yt2Doc instance by configuring and assembling various components like file cache, transcriber, and formatter based on input parameters<br>- Handles video extraction, transcription, and formatting for YouTube content, supporting both segmented and unsegmented processing modes.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/yt2doc.py'>yt2doc.py</a></b></td>
				<td>- Enables extraction and formatting of video transcripts and playlists into structured documents<br>- Uses specified extractor and formatter interfaces to process video and playlist URLs, providing formatted transcripts and playlists<br>- Logs extraction progress for each operation.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/writer.py'>writer.py</a></b></td>
				<td>- Handles writing video transcripts and playlists to Markdown files based on specified output targets<br>- Validates the output path and formats the content accordingly.</td>
			</tr>
			</table>
			<details>
				<summary><b>transcription</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/transcription/interfaces.py'>interfaces.py</a></b></td>
						<td>- Defines transcription interfaces for detecting language and transcribing audio files, as well as transcribing video chapters<br>- Interfaces include methods for language detection, audio transcription, and video chapter transcription.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/transcription/faster_whisper_adapter.py'>faster_whisper_adapter.py</a></b></td>
						<td>- Implements a FasterWhisperAdapter class that interfaces with a WhisperModel to detect language and transcribe audio files<br>- The class provides methods to transcribe audio with an initial prompt, returning segmented text data.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/transcription/whisper_cpp_adapter.py'>whisper_cpp_adapter.py</a></b></td>
						<td>- Implements a Python adapter for whisper.cpp, enabling language detection and transcription of audio files<br>- Parses whisper.cpp output to extract segments and detect language based on auto-detected codes<br>- Executes whisper.cpp commands and processes output for transcription, handling errors appropriately.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/transcription/transcriber.py'>transcriber.py</a></b></td>
						<td>- The code file `transcriber.py` facilitates audio transcription for video content, handling text cleaning, audio processing, and language detection<br>- It plays a crucial role in generating chapter-wise transcriptions by aligning audio segments with corresponding text, enhancing accessibility and searchability of video content.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>youtube</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/youtube/interfaces.py'>interfaces.py</a></b></td>
						<td>- Defines data models and interfaces for extracting YouTube video and playlist information<br>- The code specifies structures for video chapters, video details, and playlist information<br>- It also outlines methods for extracting video and audio data, as well as playlist details.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/youtube/yt_video_info_extractor.py'>yt_video_info_extractor.py</a></b></td>
						<td>- Extracts video information, merges short chapters, and extracts audio and playlist info from YouTube using yt_dlp<br>- The code enhances the project's functionality by organizing video data efficiently and providing audio extraction capabilities for a seamless user experience.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>formatting</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/formatting/interfaces.py'>interfaces.py</a></b></td>
						<td>- Defines interfaces for formatting structured transcripts and playlists, enabling seamless integration with the extraction module<br>- The code establishes protocols for segmenting topics and formatting transcripts and playlists, ensuring consistent output for downstream processing.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/formatting/formatter.py'>formatter.py</a></b></td>
						<td>Formats chaptered transcripts and playlists into a structured markdown document for easy readability and navigation within the project architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/formatting/llm_topic_segmenter.py'>llm_topic_segmenter.py</a></b></td>
						<td>- The code file orchestrates the segmentation of text into distinct chapters based on topic changes<br>- It leverages a language model to identify paragraphs that significantly shift in subject matter, grouping them into separate chapters<br>- This process enhances the readability and organization of the content, facilitating a structured presentation of information.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>extraction</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/extraction/interfaces.py'>interfaces.py</a></b></td>
						<td>- Define data structures and interfaces for extracting and caching chaptered transcripts and playlists<br>- The code in interfaces.py specifies models like TranscriptChapter and ChapteredTranscript, along with protocols for caching and extraction operations<br>- This file plays a crucial role in defining the contract for interacting with transcript data within the project architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/extraction/file_cache.py'>file_cache.py</a></b></td>
						<td>Manages caching and retrieval of chaptered transcripts for videos based on hashed metadata, ensuring efficient storage and retrieval of structured data.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/shun-liang/yt2doc/blob/master/yt2doc/extraction/extractor.py'>extractor.py</a></b></td>
						<td>- Enables extraction and transcription of videos and playlists from YouTube<br>- Utilizes interfaces for video info extraction, transcription, and caching<br>- Extracts video info, downloads audio, transcribes, and caches transcripts<br>- Supports extracting videos by chapter and playlists by combining individual video extractions.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with yt2doc, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip


###  Installation

Install yt2doc using one of the following methods:

**Build from source:**

1. Clone the yt2doc repository:
```sh
❯ git clone https://github.com/shun-liang/yt2doc
```

2. Navigate to the project directory:
```sh
❯ cd yt2doc
```

3. Install the project dependencies:


**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r requirements.txt
```




###  Usage
Run yt2doc using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ python {entrypoint}
```


###  Testing
Run the test suite using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pytest
```


---
##  Project Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/shun-liang/yt2doc/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/shun-liang/yt2doc/issues)**: Submit bugs found or log feature requests for the `yt2doc` project.
- **💡 [Submit Pull Requests](https://github.com/shun-liang/yt2doc/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/shun-liang/yt2doc
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/shun-liang/yt2doc/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=shun-liang/yt2doc">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
