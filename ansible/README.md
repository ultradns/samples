# Getting Started

## Setup Ansible

It is recommended to install `ansible` and `requests` using `pip` inside a Python virtual environment (`venv`). In this guide, I'll be creating self-contained Ansible test ecosystem in a directory relative to my home folder called `sandbox/ansible-test-env`.

```bash
mkdir ~/sandbox/ansible-test-env && cd ~/sandbox/ansible-test-env
python3 -m venv venv
source venv/bin/activate
pip3 install ansible
```

_Note:_ There are many ways to install Ansible. You can install it system-wide using a package manager like `brew` or `apt`, or using `pipx`. This is just one approach and is largely intended for development and to provide a better understanding of Ansible's ecosystem and file structure. Please refer to [Ansible's official community documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for a more detailed breakdown of options.

### Confirm the Install

Run the following commands to verify that Ansible has been installed.

```bash
ansible --version
ansible-community --version
```

Verify that these packages are installed to your Ansible test directory using `which`.

```bash
which ansible
which python
```

You will need the path to your Python binary in a bit, so take note of that.

### Initialize a Config File

Ansible has several convenient `init` commands which will, for example, create scaffolds for roles and collections within your environment. Let's create a basic configuration file.

```bash
ansible-config init --disabled > ansible.cfg
```

The `--disabled` switch here indicates that everything will be commented out by default. We want to edit this file and change a few of the values off the bat.

#### Inventory File Path

Find the following line:

```toml
# (pathlist) Comma-separated list of Ansible inventory sources
;inventory=/etc/ansible/hosts
```

Uncomment it and change the value to `hosts`:

```toml
inventory=hosts
```

We are telling Ansible to use a file relative to it's configuration file for hosts configuration.

#### Roles Path

Next, find the following:

```toml
# (pathspec) Colon-separated paths in which Ansible will search for Roles.
;roles_path=/Users/sbarbett/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles
```

We're going to edit this and change it to `roles`:

```toml
roles_path=roles
```

#### Collections Path

Search for this:

```toml
# (pathspec) Colon-separated paths in which Ansible will search for collections content. Collections must be in nested *subdirectories*, not directly in these directories. For example, if ``COLLECTIONS_PATHS`` includes ``'{{ ANSIBLE_HOME ~ "/collections" }}'``, and you want to add ``my.collection`` to that directory, it must be saved as ``'{{ ANSIBLE_HOME} ~ "/collections/ansible_collections/my/collection" }}'``.

;collections_path=/Users/sbarbett/.ansible/collections:/usr/share/ansible/collections
```

Update the path to `collections`:

```toml
collections_path=collections
```

#### Disable Host Key Checking

Finally, find the following:

```toml
# (boolean) Set this to "False" if you want to avoid host key checking by the underlying connection plugin Ansible uses to connect to the host.
# Please read the documentation of the specific connection plugin used for details.
;host_key_checking=True
```

Simply change this to `False` to disable unwanted interactive prompts when creating `ssh` connections.

```toml
host_key_checking=False
```

### Create Folders and Inventory File

Create your `roles` and `collections` directories and a simple inventory file and define `localhost` as the managed host:

```bash
mkdir roles collections
echo -e "[test_servers]\nlocalhost ansible_connection=local" > hosts
```

In Ansible, a host is the context within which your Ansible plays will be executed. In many cases, this will just be your `localhost`, but it can also be a remote server over `ssh`. Edit the `hosts` file and add the `ansible_python_interpreter` flag to the end of your localhost directory:

```toml
[test_servers]
localhost ansible_connection=local ansible_python_interpreter=<path_to_your_venv_python_binary>
```

The `path_to_your_venv_python_binary` is the output of `which python` from earlier. It's not **required** that you set this. since Ansible will automatically **discover** your Python path, but it will display a warning at every runtime.

_Note:_ You can also disable the Python discoverer warning messages in your config by changing `interpreter_python` to `auto_silent`.

#### Adding a Remote Host

While not required to follow along with this guide, if you want to add a remote host to your `hosts` file, simply add a new line to the `test_servers` grouping.

```toml
remote_host ansible_host=<remote_host_ip_or_hostname> ansible_user=<ssh_username> ansible_ssh_private_key_file=<~/.ssh/your_key>
```

### Test Connectivity

Run the following command to verify that Ansible can communicate with your host(s):

```bash
ansible test_servers -m ping
```

#### Expected Output

```javascript
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

If you added a remote host, it will show up here since it's part of your `test_servers` group.

```javascript
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
remote_host | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.11"
    },
    "changed": false,
    "ping": "pong"
}
```

If you see a timeout or authentication error, check your SSH settings (not applicable when using `localhost`).

### Test Playbook

[Provided is a simple test playbook that prints the currently installed Python version.](./playbooks/test-playbook.yml)

Make a directory called `playbooks`, save this there and then run the following:

```bash
ansible-playbook playbooks/test-playbook.yml
```

#### Expected Output

![Screenshot of output](./img/ss1-19022025.png)

---

## Install the UltraDNS Collection

To install the UltraDNS collection, run:

```bash
ansible-galaxy collection install ultradns.ultradns
```

### Install `requests`

The UltraDNS plugins require the Python `requests` modules, so install this with `pip`:

```bash
pip install requests
```

### Set Up a Directory for Variables

It's generally good practice to keep your variables in a `group_vars` directory which is divided into subdirectories by group. If you've been following this guide, your group name is `test_servers`. So create the directory as follows:

```bash
mkdir -p group_vars/test_servers
```

This is where you'll store your vault and other variables.

#### Test Variables

Let's define some test variables for the group in `group_vars/test_servers/vars`:

```yaml
# Your UltraDNS account name
test_account_name: myaccount
# A zone that is safe for testing that will be unique to your UltraDNS account
test_zone_name: testing-out-ansible-001.xyz
# A hostname (or owner name) to use in tests
test_host_name_1: test1
```

### Store Your Credentials in Ansible Vault

To securely store your UltraDNS credentials, create a **vault-protected** YAML file:

```bash
ansible-vault create group_vars/test_servers/vault
```

You'll be prompted to set a password. Once set, a text editor will open (e.g., `nano` or `vim`). Enter the following:

```yaml
ultra_provider:
  use_test: false
  username: "<your UltraDNS username>"
  password: "<your UltraDNS password>"
```

Replace the `<your UltraDNS username>` and `<your UltraDNS password>` with your actual credentials, then save and exit the editor.

_Note:_ If you want to use UltraDNS's controlled test environment (CTE), set the `use_test` boolean to "true".

#### Creating a Password File for the Vault

When using a vault within your playbooks, you must either specify `--ask-vault-password` or `--vault-password-file`. The `--ask-vault-password` flag will cause Ansible to produce an interactive prompt, which is not ideal for automation purposes. Consequently, you may wish to store it in a file.

```bash
echo "your_vault_password_here" > ~/.vault-password
chmod 600 ~/.vault-password
```

It's ill-advised that you store this in your Ansible environment. Use your home directory (or anywhere it won't accidentally get committed to a version control repository).

You can specify this directory in your `ansible.cfg`, which I suggest doing:

```toml
# (path) The vault password file to use. Equivalent to ``--vault-password-file`` or ``--vault-id``.
# If executable, it will be run and the resulting stdout will be used as the password.
;vault_password_file=
```

### Test UltraDNS Integration

The `create-zone.yml` [playbook](./playbooks/create-zone.yml) will attempt to create a test DNS zone, verifying that authentication via Ansible Vault works correctly.

Save this to your `playbooks` then run:

```bash
ansible-playbook playbooks/create-zone.yml
```

Enter your vault password when prompted.

#### Expected Output

![Screenshot of test zone creation output](./img/ss2.png)

You should also see the newly created zone in the UltraDNS user interface.

![Screenshot of newly created test zone in UI](./img/ss3.png)