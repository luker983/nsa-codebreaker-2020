<div align="center">
    <a href="/phase1/task2"><img src="/images/skip-forward.svg" align="right"></a>
</div>

<div align="center">

# Task 1 - What's On the Drive?

[![Categories Badge](/images/Categories-Computer%20Forensics%2C%20Command%20Line%2C%20Encryption%20Tools-BrightGreen.svg)](https://shields.io/)
[![Points Badge](/images/Points-10-blue.svg)](https://shields.io/)
</div>

## Prompt

> In accordance with USSID18, a collection on an American citizen is permitted in cases where the person is reasonably believed to be held captive by a group engaged in international terrorism. As a result, we have obtained a copy of the home directory from the journalist's laptop and are hoping it will contain information that will help us to locate and rescue the hostage. Your first task is to analyze the data and files available in the journalist's home directory.
>
> Downloads:
> * [Archive of data from journalist's computer (for tasks 1 & 2) (home.zip)](https://codebreaker.ltsnet.net/files/task1/home.zip)
>
> What is the journalist's username on their computer?  
> ```
> ```
>
> Enter the file name for the encrypted file on the journalist's computer.
> ```
> ```

## Files

* [home.zip](/phase1/task1/home.zip) - Provided zip file
    - [home/](/phase1/task1/home/) - Unzipped home directory
* [solution.txt](/phase1/task1/solution.txt) - Task solution

## Solution

Unzip the provided file:

```
$ unzip home.zip
```

This extracts what looks like a standard home directory. To get the username:

```
$ ls home
SkylerHummingbird324
```

To view the file structure:

```
$ tree home
home
└── SkylerHummingbird324
    ├── Documents
    │   └── Blog-Articles
    │       ├── blogEntry1.txt
    │       ├── blogEntry2.txt
    │       └── blogIntro.txt
    ├── Downloads
    ├── Pictures
    │   ├── Pets
    │   │   ├── couchChillin.jpg
    │   │   ├── loaf.jpg
    │   │   └── shenanigans.jpg
    │   └── Travels
    │       ├── Malta
    │       │   ├── BlueGrotto.jpg
    │       │   ├── MostaDome.jpg
    │       │   └── TritonFountain.jpg
    │       └── Wales
    │           ├── heatherFields.jpg
    │           └── horseFeeding.jpg
    ├── keychain
    └── pwHints.txt

9 directories, 13 files
```

The only file without a filename extension is `keychain`. To see what type of file it is:

```
$ file home/SkylerHumminbird324/keychain
home/SkylerHummingbird324/keychain: GPG symmetrically encrypted data (AES256 cipher)
```

This confirms that `keychain` is the encrypted file we're looking for. The answer to the first question is `SkylerHummingbird324`, the answer to the second is `keychain`. So far so good! 

<div align="center">

![Proof](images/proof.png)
</div>

<div align="center">
    <a href="/phase1/task2"><img src="/images/skip-forward.svg" align="right"></a>
</div>

---
