from ast import parse
from wtforms import BooleanField, HiddenField, IntegerField, SelectField, StringField
from wtforms.widgets import TextArea

from eNMS import app
from eNMS.forms import BaseForm
from eNMS.forms.fields import (
    DictField,
    MultipleInstanceField,
    NoValidationSelectField,
    NoValidationSelectMultipleField,
    PasswordSubstitutionField,
    SubstitutionField,
)


class JobForm(BaseForm):
    template = "job"
    form_type = HiddenField(default="job")
    id = HiddenField()
    type = StringField("Service Type")
    name = StringField("Name")
    description = StringField("Description")
    python_query = StringField("Python Query")
    query_property_type = SelectField(
        "Query Property Type", choices=(("name", "Name"), ("ip_address", "IP address"))
    )
    devices = MultipleInstanceField("Devices", instance_type="Device")
    pools = MultipleInstanceField("Pools", instance_type="Pool")
    workflows = MultipleInstanceField("Workflows", instance_type="Workflow")
    waiting_time = IntegerField("Waiting time (in seconds)", default=0)
    send_notification = BooleanField("Send a notification")
    send_notification_method = SelectField(
        "Notification Method",
        choices=(
            ("mail_feedback_notification", "Mail"),
            ("slack_feedback_notification", "Slack"),
            ("mattermost_feedback_notification", "Mattermost"),
        ),
    )
    notification_header = StringField(widget=TextArea(), render_kw={"rows": 5})
    include_link_in_summary = BooleanField("Include Result Link in Summary")
    display_only_failed_nodes = BooleanField("Display only Failed Devices")
    mail_recipient = StringField("Mail Recipients (separated by comma)")
    number_of_retries = IntegerField("Number of retries", default=0)
    time_between_retries = IntegerField("Time between retries (in seconds)", default=10)
    start_new_connection = BooleanField("Start New Connection")
    skip = BooleanField("Skip")
    skip_python_query = StringField("Skip (Python Query)")
    vendor = StringField("Vendor")
    operating_system = StringField("Operating System")
    shape = SelectField(
        "Shape",
        choices=(
            ("box", "Box"),
            ("circle", "Circle"),
            ("square", "Square"),
            ("diamond", "Diamond"),
            ("triangle", "Triangle"),
            ("ellipse", "Ellipse"),
            ("database", "Database"),
        ),
    )
    size = IntegerField("Size", default=40)
    color = StringField("Color", default="#D2E5FF")
    initial_payload = DictField()
    iteration_values = StringField("Iteration Targets (Python Query)")
    iteration_variable_name = StringField(
        "Iteration Variable Name", default="iteration_value"
    )
    success_query = StringField("Success Value (Python Query)")
    query_fields = ["python_query", "skip_python_query", "iteration_values"]

    def validate(self) -> bool:
        valid_form = super().validate()
        no_recipient_error = (
            self.send_notification.data
            and self.send_notification_method.data == "mail_feedback_notification"
            and not self.mail_recipient.data
            and not app.mail_recipients
        )
        bracket_error = False
        for query_field in self.query_fields:
            field = getattr(self, query_field)
            try:
                parse(field.data)
            except Exception as exc:
                bracket_error = True
                field.errors.append(f"Wrong python expression ({exc}).")
            if "{{" in field.data and "}}" in field.data:
                bracket_error = True
                field.errors.append(
                    "You cannot use variable substitution "
                    "in a field expecting a python expression."
                )
        if no_recipient_error:
            self.mail_recipient.errors.append(
                "Please add at least one recipient for the mail notification."
            )
        return valid_form and not no_recipient_error and not bracket_error


class RunForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="run")
    id = HiddenField()


class ServiceForm(JobForm):
    form_type = HiddenField(default="service")
    credentials = SelectField(
        "Credentials",
        choices=(
            ("device", "Device Credentials"),
            ("user", "User Credentials"),
            ("custom", "Custom Credentials"),
        ),
    )
    custom_username = SubstitutionField("Custom Username")
    custom_password = PasswordSubstitutionField("Custom Password")
    multiprocessing = BooleanField("Multiprocessing")
    max_processes = IntegerField("Maximum number of processes", default=50)


class WorkflowForm(JobForm):
    form_type = HiddenField(default="workflow")
    device_targets_mode = SelectField(
        "Device Targets Mode",
        choices=(
            ("service", "Run with Workflow Targets, service by service"),
            ("device", "Run with Workflow Targets, device by device"),
            ("ignore", "Run with Service Targets"),
        ),
    )
    start_jobs = MultipleInstanceField("Workflow Entry Point(s)", instance_type="Job")
    restart_runtime = NoValidationSelectField("Restart Runtime", choices=())


class RestartWorkflowForm(BaseForm):
    action = "restartWorkflow"
    form_type = HiddenField(default="restart_workflow")
    start_jobs = MultipleInstanceField("Workflow Entry Point(s)", instance_type="Job")
    restart_runtime = NoValidationSelectField("Restart Runtime", choices=())


class LogsForm(BaseForm):
    template = "logs"
    form_type = HiddenField(default="logs")
    filter = StringField("Filter")
    runtime = NoValidationSelectField("Version", choices=())


class ResultsForm(BaseForm):
    template = "results"
    form_type = HiddenField(default="results")
    compare = BooleanField(default=False)
    view_type = SelectField(
        "View", choices=(("view", "Display as JSON"), ("text", "Display as text"))
    )
    runtime = NoValidationSelectField("Version", choices=())
    runtime_compare = NoValidationSelectField("Version", choices=())


class ServiceResultsForm(ResultsForm):
    form_type = HiddenField(default="service_results")
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())


class WorkflowResultsForm(ResultsForm):
    form_type = HiddenField(default="workflow_results")
    workflow_device = NoValidationSelectField("Device", choices=())
    workflow_device_compare = NoValidationSelectField("Device", choices=())
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())
    job = NoValidationSelectField("Job", choices=())
    job_compare = NoValidationSelectField("Job", choices=())


class DeviceResultsForm(ResultsForm):
    form_type = HiddenField(default="device_results")


class RunResultsForm(ResultsForm):
    form_type = HiddenField(default="run_results")
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())


class AddJobsForm(BaseForm):
    action = "addJobsToWorkflow"
    form_type = HiddenField(default="add_jobs")
    jobs = MultipleInstanceField("Add jobs", instance_type="Job")


class ServiceTableForm(BaseForm):
    form_type = HiddenField(default="service_table")
    services = SelectField(choices=())


class WorkflowLabelForm(BaseForm):
    form_type = HiddenField(default="workflow_label")
    action = "createLabel"
    content = StringField(widget=TextArea(), render_kw={"rows": 15})


class WorkflowEdgeForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="WorkflowEdge")
    id = HiddenField()
    label = StringField()
