### Submodules?
This repo is used as a submodule in several tkr_kit apps.
This means it's a separate git repo that can be updated/commited independently from the main repo. 

To ensure it's properly initialized use the `--recursive` flag when doing the intial clone. 

```sh
git clone --recursive http://github.com/tuckertucker/main_repo
```

### Initializing and/or Updating Submodules
If you have cloned the main repository without using the `--recursive` flag, 
Here's how you can manually initialize and update the submodules. 

    1. Navigate to the cloned main repository directory
    2. Run the following command to initialize and update submodule(s)

    ```sh
    git submodule update --init --recursive
    ```