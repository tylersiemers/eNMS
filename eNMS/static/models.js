class Base {
  constructor(properties) {
    Object.assign(this, properties);
  }

  static createNewButton(type) {
    return `
      <button
        class="btn btn-primary"
        onclick="eNMS.showTypePanel('${type}')"
        data-tooltip="New"
        type="button"
      >
        <span class="glyphicon glyphicon-plus"></span>
      </button>`;
  }

  static searchTableButton(type) {
    return `
      <button
        class="btn btn-info btn-file"
        onclick="eNMS.showPanel('${type}_filtering')"
        data-tooltip="Advanced Search"
        type="button"
      >
        <span class="glyphicon glyphicon-search"></span>
      </button>`;
  }

  static refreshTableButton(type) {
    return `
      <button
        class="btn btn-info btn-file"
        onclick="eNMS.refreshTable('${type}', true)"
        data-tooltip="Refresh"
        type="button"
      >
        <span class="glyphicon glyphicon-refresh"></span>
      </button>`;
  }
}

class Device extends Base {
  static get columns() {
    return [
      { data: "name", title: "Name", search: "text" },
      { data: "description", title: "Description", search: "text" },
      { data: "subtype", title: "Subtype", search: "text" },
      { data: "model", title: "Model", search: "text" },
      { data: "location", title: "Location", search: "text" },
      { data: "vendor", title: "Vendor", search: "text" },
      { data: "operating_system", title: "Operating System", search: "text" },
      { data: "os_version", title: "OS Version", search: "text" },
      { data: "ip_address", title: "IP Address", search: "text" },
      { data: "port", title: "Port", search: "text" },
      { data: "buttons" },
    ];
  }

  static get controls() {
    return [
      super.createNewButton("device"),
      super.searchTableButton("device"),
      super.refreshTableButton("device"),
    ];
  }

  get buttons() {
    const instance = JSON.stringify(this);
    return `
      <ul class="pagination pagination-lg" style="margin: 0px; width: 230px">
        <li>
          <button type="button" class="btn btn-sm btn-info"
          onclick='eNMS.showDeviceNetworkData(${instance})'
          data-tooltip="Network Data"
            ><span class="glyphicon glyphicon-cog"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-info"
          onclick="showDeviceResultsPanel(${instance})"
          data-tooltip="Results"
            ><span class="glyphicon glyphicon-list-alt"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-success"
          onclick="eNMS.showPanel('device_connection', '${this.id}')"
          data-tooltip="Connection"
            ><span class="glyphicon glyphicon-console"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('device', '${
            this.id
          }')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('device', '${this.id}', 'duplicate')"
          data-tooltip="Duplicate"
            ><span class="glyphicon glyphicon-duplicate"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-danger"
          onclick="showDeletionPanel(${instance})" data-tooltip="Delete"
            ><span class="glyphicon glyphicon-trash"></span
          ></button>
        </li>
      </ul>`;
  }
}

class Link extends Base {
  static get columns() {
    return [
      { data: "name", title: "Name", search: "text" },
      { data: "description", title: "Description", search: "text" },
      { data: "subtype", title: "Subtype", search: "text" },
      { data: "model", title: "Model", search: "text" },
      { data: "location", title: "Location", search: "text" },
      { data: "vendor", title: "Vendor", search: "text" },
      { data: "source_name", title: "Source", search: "text" },
      { data: "destination_name", title: "Destination", search: "text" },
      { data: "buttons" },
    ];
  }

  static get controls() {
    return [
      super.createNewButton("link"),
      super.searchTableButton("link"),
      super.refreshTableButton("link"),
    ];
  }

  get buttons() {
    const instance = JSON.stringify(this);
    return `
      <ul class="pagination pagination-lg" style="margin: 0px; width: 120px">
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('link', '${this.id}')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('link', '${this.id}', 'duplicate')"
          data-tooltip="Duplicate"
            ><span class="glyphicon glyphicon-duplicate"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-danger"
          onclick='showDeletionPanel(${instance})' data-tooltip="Delete"
            ><span class="glyphicon glyphicon-trash"></span
          ></button>
        </li>
      </ul>`;
  }
}

class Pool extends Base {
  static get columns() {
    return [
      { data: "name", title: "Name", search: "text" },
      { data: "last_modified", title: "Last modified", search: "text" },
      { data: "description", title: "Description", search: "text" },
      { data: "never_update", title: "Never update", search: "bool" },
      { data: "longitude", title: "Longitude", search: "text" },
      { data: "latitude", title: "Latitude", search: "text" },
      { data: "object_number", title: "Object Count" },
      { data: "buttons" },
    ];
  }

  get object_number() {
    return `${this.device_number} devices - ${this.link_number} links`;
  }

  get buttons() {
    const instance = JSON.stringify(this);
    return `
      <ul class="pagination pagination-lg" style="margin: 0px; width: 230px">
        <li>
          <button type="button" class="btn btn-sm btn-info"
          onclick="showPoolView('${this.id}')" data-tooltip="Internal View"
            ><span class="glyphicon glyphicon-eye-open"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="showPoolObjectsPanel('${
            this.id
          }')" data-tooltip="Pool Objects"
            ><span class="glyphicon glyphicon-wrench"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="updatePools('${this.id}')" data-tooltip="Update"
            ><span class="glyphicon glyphicon-refresh"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('pool', '${this.id}')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('pool', '${this.id}', 'duplicate')"
          data-tooltip="Duplicate"
            ><span class="glyphicon glyphicon-duplicate"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-danger"
          onclick="showDeletionPanel(${instance})" data-tooltip="Delete"
            ><span class="glyphicon glyphicon-trash"></span
          ></button>
        </li>
      </ul>
    `;
  }
}

class Service extends Base {
  static get columns() {
    return [
      {
        data: "name",
        title: "Name",
        search: "text",
        render: function(data, type, row, meta) {
          return `<b><a href="#" onclick="eNMS.switchToWorkflow('${row.id}')">${
            row.scoped_name
          }</a></b>`;
        },
      },
      { data: "last_modified", title: "Last modified", search: "text" },
      { data: "type", title: "Type", search: "text" },
      { data: "description", title: "Description", search: "text" },
      { data: "vendor", title: "Vendor", search: "text" },
      { data: "operating_system", title: "Operating System", search: "text" },
      { data: "creator", title: "Creator", search: "text" },
      { data: "creator", title: "Creator", search: "text" },
      { data: "status", title: "Status", search: "text" },
      { data: "buttons" },
    ];
  }

  static get controls() {
    return `
      <button
        class="btn btn-primary"
        onclick="eNMS.openServicePanel()"
        data-tooltip="New"
        type="button"
      >
        <span class="glyphicon glyphicon-plus"></span>
      </button>
      <button
        class="btn btn-info btn-file"
        onclick="eNMS.showPanel('service_filtering')"
        data-tooltip="Advanced Search"
        type="button"
      >
        <span class="glyphicon glyphicon-search"></span>
      </button>
      <button
        class="btn btn-info btn-file"
        onclick="eNMS.refreshTable('service', true)"
        data-tooltip="Refresh"
        type="button"
      >
        <span class="glyphicon glyphicon-refresh"></span>
      </button>
      <a
      id="left-arrow"
      class="btn btn-info btn-file"
      onclick="action['Backward']()"
      type="button"
    >
      <span class="glyphicon glyphicon-chevron-left"></span>
    </a>
    <a
      id="right-arrow"
      class="btn btn-info btn-file"
      onclick="action['Forward']()"
      type="button"
    >
      <span class="glyphicon glyphicon-chevron-right"></span>
    </a>
    <div class="pull-right">
      <select
        id="parent-filtering"
        name="parent-filtering"
        class="form-control"
      >
        <option value="true">Display services hierarchically</option>
        <option value="false">Display all services</option>
      </select>
    </div>
    <input type="hidden" id="workflow-filtering" name="workflow-filtering">
      `;
  }

  get status() {
    return "Idle";
  }

  get buttons() {
    const instance = JSON.stringify(this);
    return `
      <ul class="pagination pagination-lg" style="margin: 0px; width: 270px">
        <li>
          <button type="button" class="btn btn-sm btn-info"
          onclick="showRuntimePanel('results', ${instance})"
          data-tooltip="Results"><span class="glyphicon glyphicon-list-alt"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-info"
          onclick="showRuntimePanel('logs', ${instance})"
          data-tooltip="Logs"><span class="glyphicon glyphicon-list"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-success"
          onclick="normalRun('${this.id}')" data-tooltip="Run"
            ><span class="glyphicon glyphicon-play"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-success"
          onclick="eNMS.showTypePanel('{self.type}', '${this.id}', 'run')"
          data-tooltip="Parameterized Run"
            ><span class="glyphicon glyphicon-play-circle"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.showTypePanel('{self.type}', '${
            this.id
          }')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="exportService('${this.id}')" data-tooltip="Export"
            ><span class="glyphicon glyphicon-download"></span
          ></button>
        </li>
        <li>
          <button type="button" class="btn btn-sm btn-danger"
          onclick="showDeletionPanel(${instance})" data-tooltip="Delete"
            ><span class="glyphicon glyphicon-trash"></span
          ></button>
        </li>
      </ul>
    `;
  }
}

const models = {
  device: Device,
  link: Link,
  pool: Pool,
  service: Service,
};

export default models;