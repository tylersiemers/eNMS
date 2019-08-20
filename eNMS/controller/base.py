from apscheduler.schedulers.background import BackgroundScheduler
from collections import Counter
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from flask import Flask
from flask_login import current_user
from git import Repo
from hvac import Client as VaultClient
from importlib import import_module
from importlib.abc import Loader
from importlib.util import spec_from_file_location, module_from_spec
from json import load
from ldap3 import ALL, Server
from logging import basicConfig, error, info, StreamHandler, warning
from logging.handlers import RotatingFileHandler
from os import environ, remove, scandir
from pathlib import Path
from ruamel import yaml
from simplekml import Color, Style
from smtplib import SMTP
from string import punctuation
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError, InterfaceError, InvalidRequestError
from sqlalchemy.orm import configure_mappers
from sys import path as sys_path
from tacacs_plus.client import TACACSClient
from typing import Any, Dict, List, Optional, Set, Union
from uuid import getnode
from werkzeug.datastructures import ImmutableMultiDict

from eNMS.database import Base, DIALECT, engine, Session
from eNMS.database.functions import count, delete, factory, fetch, fetch_all
from eNMS.framework import create_app
from eNMS.models import models, model_properties, relationships
from eNMS.properties import private_properties, property_names
from eNMS.properties.database import import_classes
from eNMS.properties.diagram import (
    device_diagram_properties,
    diagram_classes,
    type_to_diagram_properties,
)
from eNMS.properties.table import filtering_properties, table_properties
from eNMS.properties.objects import (
    device_properties,
    device_icons,
    pool_device_properties,
)
from eNMS.controller.syslog import SyslogServer


class BaseController:

    cluster = int(environ.get("CLUSTER", False))
    cluster_id = int(environ.get("CLUSTER_ID", True))
    cluster_scan_subnet = environ.get("CLUSER_SCAN_SUBNET", "192.168.105.0/24")
    cluster_scan_protocol = environ.get("CLUSTER_SCAN_PROTOCOL", "http")
    cluster_scan_timeout = environ.get("CLUSTER_SCAN_TIMEOUT", 0.05)
    config_mode = environ.get("CONFIG_MODE", "Debug")
    custom_code_path = environ.get("CUSTOM_CODE_PATH")
    default_longitude = environ.get("DEFAULT_LONGITUDE", -96.0)
    default_latitude = environ.get("DEFAULT_LATITUDE", 33.0)
    default_zoom_level = environ.get("DEFAULT_ZOOM_LEVEL", 5)
    default_view = environ.get("DEFAULT_VIEW", "2D")
    default_marker = environ.get("DEFAULT_MARKER", "Image")
    documentation_url = environ.get(
        "DOCUMENTATION_URL", "https://enms.readthedocs.io/en/latest/"
    )
    create_examples = int(environ.get("CREATE_EXAMPLES", True))
    custom_services_path = environ.get("CUSTOM_SERVICES_PATH")
    log_level = environ.get("LOG_LEVEL", "DEBUG")
    server_addr = environ.get("SERVER_ADDR", "http://SERVER_IP")
    git_automation = environ.get("GIT_AUTOMATION")
    git_configurations = environ.get("GIT_CONFIGURATIONS")
    gotty_port_redirection = int(environ.get("GOTTY_PORT_REDIRECTION", False))
    gotty_bypass_key_prompt = int(environ.get("GOTTY_BYPASS_KEY_PROMPT", False))
    gotty_port = -1
    gotty_start_port = int(environ.get("GOTTY_START_PORT", 9000))
    gotty_end_port = int(environ.get("GOTTY_END_PORT", 9100))
    ldap_server = environ.get("LDAP_SERVER")
    ldap_userdn = environ.get("LDAP_USERDN")
    ldap_basedn = environ.get("LDAP_BASEDN")
    ldap_admin_group = environ.get("LDAP_ADMIN_GROUP", "")
    mail_server = environ.get("MAIL_SERVER", "smtp.googlemail.com")
    mail_port = int(environ.get("MAIL_PORT", "587"))
    mail_use_tls = int(environ.get("MAIL_USE_TLS", True))
    mail_username = environ.get("MAIL_USERNAME")
    mail_password = environ.get("MAIL_PASSWORD")
    mail_sender = environ.get("MAIL_SENDER", "enms@enms.fr")
    mail_recipients = environ.get("MAIL_RECIPIENTS", "")
    mattermost_url = environ.get("MATTERMOST_URL")
    mattermost_channel = environ.get("MATTERMOST_CHANNEL")
    mattermost_verify_certificate = int(
        environ.get("MATTERMOST_VERIFY_CERTIFICATE", True)
    )
    opennms_login = environ.get("OPENNMS_LOGIN")
    opennms_devices = environ.get("OPENNMS_DEVICES", "")
    opennms_rest_api = environ.get("OPENNMS_REST_API")
    playbook_path = environ.get("PLAYBOOK_PATH")
    pool_filter = environ.get("POOL_FILTER", "All objects")
    slack_token = environ.get("SLACK_TOKEN")
    slack_channel = environ.get("SLACK_CHANNEL")
    syslog_addr = environ.get("SYSLOG_ADDR", "0.0.0.0")
    syslog_port = int(environ.get("SYSLOG_PORT", 514))
    tacacs_addr = environ.get("TACACS_ADDR")
    tacacs_password = environ.get("TACACS_PASSWORD")
    unseal_vault = environ.get("UNSEAL_VAULT")
    use_ldap = int(environ.get("USE_LDAP", False))
    use_syslog = int(environ.get("USE_SYSLOG", False))
    use_tacacs = int(environ.get("USE_TACACS", False))
    use_vault = int(environ.get("USE_VAULT", False))
    vault_addr = environ.get("VAULT_ADDR")

    log_severity = {"error": error, "info": info, "warning": warning}

    free_access_pages = ["/", "/login"]

    valid_pages = [
        "/administration",
        "/calendar/run",
        "/calendar/task",
        "/dashboard",
        "/login",
        "/table/changelog",
        "/table/configuration",
        "/table/device",
        "/table/event",
        "/table/pool",
        "/table/link",
        "/table/run",
        "/table/server",
        "/table/service",
        "/table/syslog",
        "/table/task",
        "/table/user",
        "/table/workflow",
        "/view/network",
        "/view/site",
        "/workflow_builder",
    ]

    valid_post_endpoints = [
        "add_edge",
        "add_jobs_to_workflow",
        "calendar_init",
        "clear_results",
        "clear_configurations",
        "compare_results",
        "connection",
        "counters",
        "count_models",
        "database_deletion",
        "delete_edge",
        "delete_instance",
        "delete_node",
        "duplicate_workflow",
        "export_job",
        "export_to_google_earth",
        "export_topology",
        "filtering",
        "get",
        "get_all",
        "get_cluster_status",
        "get_configurations",
        "get_configuration_diff",
        "get_device_list",
        "get_device_logs",
        "get_exported_jobs",
        "get_git_content",
        "get_job_list",
        "get_job_logs",
        "get_properties",
        "get_results",
        "get_results_diff",
        "get_runtimes",
        "get_view_topology",
        "get_workflow_device_list",
        "get_workflow_state",
        "import_jobs",
        "import_topology",
        "migration_export",
        "migration_import",
        "query_netbox",
        "query_librenms",
        "query_opennms",
        "reset_status",
        "restart_workflow",
        "run_job",
        "save_parameters",
        "save_pool_objects",
        "save_positions",
        "scan_cluster",
        "scan_playbook_folder",
        "scheduler",
        "task_action",
        "topology_import",
        "update",
        "update_parameters",
        "update_pool",
        "update_all_pools",
        "view_filtering",
    ]

    valid_rest_endpoints = [
        "get_cluster_status",
        "get_git_content",
        "update_all_pools",
        "update_database_configurations_from_git",
    ]

    def __init__(self) -> None:
        self.custom_properties = self.load_custom_properties()
        self.custom_config = self.load_custom_config()
        self.init_scheduler()
        if self.use_tacacs:
            self.init_tacacs_client()
        if self.use_ldap:
            self.init_ldap_client()
        if self.use_vault:
            self.init_vault_client()
        if self.use_syslog:
            self.init_syslog_server()
        if self.custom_code_path:
            sys_path.append(self.custom_code_path)

    def create_google_earth_styles(self) -> None:
        self.google_earth_styles: Dict[str, Style] = {}
        for icon in device_icons:
            point_style = Style()
            point_style.labelstyle.color = Color.blue
            path_icon = f"{self.path}/eNMS/static/images/2D/{icon}.gif"
            point_style.iconstyle.icon.href = path_icon
            self.google_earth_styles[icon] = point_style

    def fetch_version(self) -> None:
        with open(self.path / "package.json") as package_file:
            self.version = load(package_file)["version"]

    def configure_database(self, app: Flask) -> None:
        Base.metadata.create_all(bind=engine)
        from eNMS.database.events import configure_events

        configure_events(self)
        configure_mappers()

        @app.before_first_request
        def initialize_database() -> None:
            self.clean_database()
            if not fetch("User", allow_none=True, name="admin"):
                self.init_database()

    def init_parameters(self) -> None:
        parameters = Session.query(models["Parameters"]).one_or_none()
        if not parameters:
            parameters = models["Parameters"]()
            parameters.update(
                **{
                    property: getattr(self, property)
                    for property in model_properties["Parameters"]
                    if hasattr(self, property)
                }
            )
            Session.add(parameters)
            Session.commit()
        else:
            for parameter in parameters.get_properties():
                setattr(self, parameter, getattr(parameters, parameter))

    def configure_server_id(self) -> None:
        factory(
            "Server",
            **{
                "name": str(getnode()),
                "description": "Localhost",
                "ip_address": "0.0.0.0",
                "status": "Up",
            },
        )

    def create_admin_user(self) -> None:
        factory("User", **{"name": "admin", "password": "admin"})

    def update_credentials(self) -> None:
        with open(self.path / "projects" / "spreadsheets" / "usa.xls", "rb") as file:
            self.topology_import(file)  # type: ignore

    def clean_database(self) -> None:
        for run in fetch("Run", all_matches=True, allow_none=True, status="Running"):
            run.status = "Aborted (app reload)"
        Session.commit()

    def init_database(self) -> None:
        self.init_parameters()
        self.configure_server_id()
        self.create_admin_user()
        Session.commit()
        if self.create_examples:
            self.migration_import(
                name="examples", import_export_types=import_classes
            )  # type: ignore
            self.update_credentials()
        else:
            self.migration_import(
                name="default", import_export_types=import_classes
            )  # type: ignore
        self.get_git_content()
        Session.commit()

    def init_app(self, path: Path, config_mode: Optional[str] = None) -> Flask:
        self.path = path
        if config_mode:
            self.config_mode = config_mode
        self.init_services()
        app = create_app(self)
        self.configure_database(app)
        self.init_forms()
        self.create_google_earth_styles()
        self.fetch_version()
        self.init_logs()
        return app

    @property
    def config(self) -> dict:
        parameters = Session.query(models["Parameters"]).one_or_none()
        return parameters.get_properties() if parameters else {}

    def get_git_content(self) -> None:
        for repository_type in ("configurations", "automation"):
            repo = getattr(self, f"git_{repository_type}")
            if not repo:
                continue
            local_path = self.path / "git" / repository_type
            repo_contents_exist = False
            for entry in scandir(local_path):
                if entry.name == ".gitkeep":
                    remove(entry)
                if entry.name == ".git":
                    repo_contents_exist = True
            if repo_contents_exist:
                try:
                    Repo(local_path).remotes.origin.pull()
                    if repository_type == "configurations":
                        self.update_database_configurations_from_git()
                except Exception as e:
                    info(f"Cannot pull {repository_type} git repository ({str(e)})")
            else:
                try:
                    Repo.clone_from(repo, local_path)
                    if repository_type == "configurations":
                        self.update_database_configurations_from_git()
                except Exception as e:
                    info(f"Cannot clone {repository_type} git repository ({str(e)})")

    def load_custom_config(self) -> dict:
        filepath = environ.get("PATH_CUSTOM_CONFIG")
        if not filepath:
            return {}
        else:
            with open(filepath, "r") as config:
                return load(config)

    def load_custom_properties(self) -> dict:
        filepath = environ.get("PATH_CUSTOM_PROPERTIES")
        if not filepath:
            custom_properties: dict = {}
        else:
            with open(filepath, "r") as properties:
                custom_properties = yaml.load(properties)
        property_names.update(
            {k: v["pretty_name"] for k, v in custom_properties.items()}
        )
        public_custom_properties = {
            k: v for k, v in custom_properties.items() if not v.get("private", False)
        }
        device_properties.extend(list(custom_properties))
        pool_device_properties.extend(list(public_custom_properties))
        for properties_table in table_properties, filtering_properties:
            properties_table["device"].extend(list(public_custom_properties))
        device_diagram_properties.extend(
            list(p for p, v in custom_properties.items() if v["add_to_dashboard"])
        )
        private_properties.extend(
            list(p for p, v in custom_properties.items() if v.get("private", False))
        )
        return custom_properties

    def init_logs(self) -> None:
        basicConfig(
            level=getattr(import_module("logging"), self.log_level),
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%m-%d-%Y %H:%M:%S",
            handlers=[
                RotatingFileHandler(
                    self.path / "logs" / "enms.log", maxBytes=20_000_000, backupCount=10
                ),
                StreamHandler(),
            ],
        )

    def init_scheduler(self) -> None:
        self.scheduler = BackgroundScheduler(
            {
                "apscheduler.jobstores.default": {
                    "type": "sqlalchemy",
                    "url": "sqlite:///jobs.sqlite",
                },
                "apscheduler.executors.default": {
                    "class": "apscheduler.executors.pool:ThreadPoolExecutor",
                    "max_workers": "50",
                },
                "apscheduler.job_defaults.misfire_grace_time": "5",
                "apscheduler.job_defaults.coalesce": "true",
                "apscheduler.job_defaults.max_instances": "3",
            }
        )

        self.scheduler.start()

    def init_forms(self) -> None:
        for file in (self.path / "eNMS" / "forms").glob("**/*.py"):
            spec = spec_from_file_location(str(file).split("/")[-1][:-3], str(file))
            spec.loader.exec_module(module_from_spec(spec))  # type: ignore

    def init_services(self) -> None:
        path_services = [self.path / "eNMS" / "services"]
        if self.custom_services_path:
            path_services.append(Path(self.custom_services_path))
        for path in path_services:
            for file in path.glob("**/*.py"):
                if "init" in str(file):
                    continue
                if not self.create_examples and "examples" in str(file):
                    continue
                spec = spec_from_file_location(str(file).split("/")[-1][:-3], str(file))
                assert isinstance(spec.loader, Loader)
                module = module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                except InvalidRequestError as e:
                    error(f"Error loading custom service '{file}' ({str(e)})")

    def init_ldap_client(self) -> None:
        self.ldap_client = Server(self.ldap_server, get_info=ALL)

    def init_tacacs_client(self) -> None:
        self.tacacs_client = TACACSClient(self.tacacs_addr, 49, self.tacacs_password)

    def init_vault_client(self) -> None:
        self.vault_client = VaultClient()
        self.vault_client.url = self.vault_addr
        self.vault_client.token = environ.get("VAULT_TOKEN")
        if self.vault_client.sys.is_sealed() and self.unseal_vault:
            keys = [environ.get(f"UNSEAL_VAULT_KEY{i}") for i in range(1, 6)]
            self.vault_client.sys.submit_unseal_keys(filter(None, keys))

    def init_syslog_server(self) -> None:
        self.syslog_server = SyslogServer(self.syslog_addr, self.syslog_port)
        self.syslog_server.start()

    def update_parameters(self, **kwargs: Any) -> None:
        Session.query(models["Parameters"]).one().update(**kwargs)
        self.__dict__.update(**kwargs)

    def delete_instance(self, cls: str, instance_id: int) -> dict:
        return delete(cls, id=instance_id)

    def get(self, cls: str, id: str) -> dict:
        return fetch(cls, id=id).serialized

    def get_properties(self, cls: str, id: str) -> dict:
        return fetch(cls, id=id).get_properties()

    def get_all(self, cls: str) -> List[dict]:
        return [instance.get_properties() for instance in fetch_all(cls)]

    def update(self, cls: str, **kwargs: Any) -> dict:
        try:
            must_be_new = kwargs.get("id") == ""
            kwargs["last_modified"] = self.get_time()
            kwargs["creator"] = getattr(current_user, "name", "admin")
            instance = factory(cls, must_be_new=must_be_new, **kwargs)
            Session.flush()
            return instance.serialized
        except Exception as exc:
            Session.rollback()
            if isinstance(exc, IntegrityError):
                return {"error": (f"There already is a {cls} with the same name")}
            return {"error": str(exc)}

    def log(self, severity: str, content: str) -> None:
        factory(
            "Changelog",
            **{
                "severity": severity,
                "content": content,
                "user": getattr(current_user, "name", "admin"),
            },
        )
        self.log_severity[severity](content)

    def count_models(self) -> dict:
        return {
            "counters": {cls: count(cls) for cls in diagram_classes},
            "properties": {
                cls: Counter(
                    str(getattr(instance, type_to_diagram_properties[cls][0]))
                    for instance in fetch_all(cls)
                )
                for cls in diagram_classes
            },
        }

    def filtering(self, table: str, kwargs: ImmutableMultiDict) -> dict:
        model = models.get(table, models["Device"])
        properties = table_properties[table]
        operator = and_ if kwargs.get("form[operator]", "all") == "all" else or_
        try:
            order_property = properties[int(kwargs["order[0][column]"])]
        except IndexError:
            order_property = "name"
        order = getattr(getattr(model, order_property), kwargs["order[0][dir]"])()
        constraints = []
        for property in filtering_properties[table]:
            value = kwargs.get(f"form[{property}]")
            if not value:
                continue
            filter = kwargs.get(f"form[{property}_filter]")
            if filter == "equality":
                constraint = getattr(model, property) == value
            elif filter == "inclusion" or DIALECT == "sqlite":
                constraint = getattr(model, property).contains(value)
            else:
                regex_operator = "regexp" if DIALECT == "mysql" else "~"
                constraint = getattr(model, property).op(regex_operator)(value)
            constraints.append(constraint)
        relation = table.capitalize() if table != "configuration" else "Device"
        for related_model, relation_properties in relationships[relation].items():
            relation_ids = [
                int(id) for id in kwargs.getlist(f"form[{related_model}][]")
            ]
            if not relation_ids:
                continue
            if relation_properties["list"]:
                constraint = getattr(model, related_model).any(
                    models[relation_properties["model"]].id.in_(relation_ids)
                )
            else:
                constraint = or_(
                    getattr(model, related_model).has(id=relation_id)
                    for relation_id in relation_ids
                )
            constraints.append(constraint)
        result = Session.query(model).filter(operator(*constraints)).order_by(order)
        try:
            return {
                "draw": int(kwargs["draw"]),
                "recordsTotal": len(Session.query(model).all()),
                "recordsFiltered": len(result.all()),
                "data": [
                    [getattr(obj, property) for property in properties]
                    + obj.generate_row(table)
                    for obj in result.limit(int(kwargs["length"]))
                    .offset(int(kwargs["start"]))
                    .all()
                ],
            }
        except InterfaceError:
            return {"error": "Filtering error: wrong input"}

    def allowed_file(self, name: str, allowed_modules: Set[str]) -> bool:
        allowed_syntax = "." in name
        allowed_extension = name.rsplit(".", 1)[1].lower() in allowed_modules
        return allowed_syntax and allowed_extension

    def get_time(self) -> str:
        return str(datetime.now())

    def send_email(
        self,
        subject: str,
        content: str,
        sender: Optional[str] = None,
        recipients: Optional[str] = None,
        filename: Optional[str] = None,
        file_content: Optional[Union[str, bytes]] = None,
    ) -> None:
        sender = sender or self.mail_sender
        recipients = recipients or self.mail_recipients
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipients
        message["Date"] = formatdate(localtime=True)
        message["Subject"] = subject
        message.attach(MIMEText(content))
        if filename:
            assert file_content
            attached_file = MIMEApplication(file_content, Name=filename)
            attached_file["Content-Disposition"] = f'attachment; filename="{filename}"'
            message.attach(attached_file)
        server = SMTP(self.mail_server, self.mail_port)
        if self.mail_use_tls:
            assert self.mail_username and self.mail_password
            server.starttls()
            server.login(self.mail_username, self.mail_password)
        server.sendmail(sender, recipients.split(","), message.as_string())
        server.close()

    def str_dict(self, input: Any, depth: int = 0) -> str:
        tab = "\t" * depth
        if isinstance(input, list):
            result = "\n"
            for element in input:
                result += f"{tab}- {self.str_dict(element, depth + 1)}\n"
            return result
        elif isinstance(input, dict):
            result = ""
            for key, value in input.items():
                result += f"\n{tab}{key}: {self.str_dict(value, depth + 1)}"
            return result
        else:
            return str(input)

    def strip_all(self, input: str) -> str:
        return input.translate(str.maketrans("", "", f"{punctuation} "))

    def update_database_configurations_from_git(self) -> None:
        for dir in scandir(self.path / "git" / "configurations"):
            if dir.name == ".git":
                continue
            device = fetch("Device", allow_none=True, name=dir.name)
            if device:
                with open(Path(dir.path) / "data.yml") as data:
                    parameters = yaml.load(data)
                    device.update(**parameters)
                    config_file = Path(dir.path) / dir.name
                    if not config_file.exists():
                        continue
                    with open(config_file) as f:
                        device.current_configuration = device.configurations[
                            str(parameters["last_update"])
                        ] = f.read()
        Session.commit()
        for pool in fetch_all("Pool"):
            if pool.device_current_configuration:
                pool.compute_pool()
