import React, { Component } from 'react';
import 'regenerator-runtime/runtime';
import { react2angular } from 'react2angular';
import axios from 'axios';
import throttle from 'lodash.throttle';

import Select from 'react-select';
import AsyncCreatable from 'react-select/lib/Async';

import { EMAIL_REGEX, VARIABLE_REGEX, TYPED_TEXT_REGEX } from './constants';
import LilyEditor from './LilyEditor.jsx';

function convertKeys(data) {
  Object.keys(data).forEach(key => {
    const convertedKey = convertKey(key);

    if (convertedKey !== key) {
      data[convertedKey] = data[key];
      // Delete the old key since we don't want pollute our data with unused keys.
      delete data[key];
    }

    if (data[convertedKey] !== null && typeof data[convertedKey] === 'object') {
      data[convertedKey] = convertKeys(data[convertedKey]);
    }
  });

  return data;
}

function convertKey(key, toSnakeCase = false) {
  let convertedKey = key;

  if (toSnakeCase) {
    // Since the back end uses snake_case, we also want to convert fields back when sending data.
    convertedKey = convertedKey.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase();
  } else {
    const splitKey = key.split('_');
    convertedKey = splitKey[0];

    // Convert to camelCase.
    if (splitKey.length > 1) {
      for (let i = 1; i < splitKey.length; i++) {
        convertedKey += splitKey[i].charAt(0).toUpperCase() + splitKey[i].slice(1);
      }
    }
  }

  return convertedKey;
}

axios.defaults.transformResponse = [(data, headers) => {
  const json = JSON.parse(data);

  // To clean up the front-end code we want to use our own code style (so camelCase).
  return convertKeys(json);
}];

// axios.defaults.transformRequest = [(data, headers) => {
//   // Convert keys back to snake_case.
//   return JSON.stringify(convertKeys(data));
// }];

const styles = {
  control: (base, state) => ({
    ...base,
    background: '#fff',
    border: 'none'
  }),
}

class EmailEditor extends Component {
  constructor(props) {
    super(props);

    // TODO: TEMPORARY.
    const user = window.currentUser;

    this.state = {
      user,
      subject: '',
      modalOpen: false
    };
  }

  componentDidMount = async () => {
    const { email, recipients = [], documentId } = this.props;

    const state = {
      recipients: [],
      recipientsCc: [],
      recipientsBcc: []
    };

    if (email) {
      state.recipients.push({ value: email, label: email });
    }

    if (recipients) {
      recipients.forEach((recipient, index) => {
        // TODO: Temporary, since our conversion should happen for every request, not just axios requests.
        delete recipient.$promise;
        delete recipient.$resolved;
        recipient = convertKeys(recipient);

        const data = {
          value: recipient,
          label: this.createRecipientLabel(recipient.emailAddress, recipient.fullName)
        };

        if (index > 1) {
          // More than 1 recipient so it's most likely a reply all.
          state.recipientsCc.push(data);
        } else {
          state.contact = recipient;
          state.recipients.push(data);
        }
      });
    }

    let initialTemplate = this.props.template;

    const accountRequest = await this.getEmailAccounts();

    const emailAccounts = accountRequest.data.results.map(account => {
      const label = `${account.label} (${account.emailAddress})`;

      return { value: account, label };
    });

    // If an initial email account passed load it.
    // Otherwise check if the user has set a primary email account.
    const initialEmailAccount = this.props.emailAccount || this.state.user.primaryEmailAccount;

    if (initialEmailAccount) {
      const emailAccount = emailAccounts.find(account => account.value.id === initialEmailAccount);

      state.emailAccount = emailAccount;

      if (emailAccount.defaultTemplate) {
        initialTemplate = emailAccount.defaultTemplate.id;
      }
    }

    state.emailAccounts = emailAccounts;

    const templateRequest = await this.getEmailTemplates();
    const templates = templateRequest.data.results.map(template => {
      return { value: template, label: template.name };
    });

    // A template was passed to the editor component, so load that instead of the default.
    if (this.props.loadDefaultTemplate && initialTemplate) {
      const template = templates.find(template => template.value.id === initialTemplate);

      state.template = template;

      // TODO: Implement check to see if the message is a reply.
      // const subject = this.props.messageType === NEW_MESSAGE ? subject : this.state.message.subject;
      const subject = template.value.subject;
      state.subject = subject;

      this.loadTemplate(template.value.bodyHtml, subject, template.value.customVariables);
    }

    state.templates = templates;

    if (documentId && state.recipients.length > 0) {
      try {
        const documentRequest = await this.getDocument(documentId, state.recipients[0].value.emailAddress);

        state.document = documentRequest.data.document;
      } catch(error) {
        // TODO: Show some sort of notification to the user.
        alert('Document couldn\'t be loaded');
        console.log(error.response.data.error);
      }
    }

    this.setState(state);
  }

  async getEmailAccounts() {
    return axios.get(`/api/messaging/email/accounts/`);
  }

  async getEmailTemplates() {
    return axios.get(`/api/messaging/email/templates/`);
  }

  async getContacts() {
    return axios.get(`/api/contacts/`);
  }

  getRecipients = async query => {
    const searchQuery = query ? `?search=first_name:${query}` : '';
    const contactRequest = await axios.get(`/api/contacts/${searchQuery}`);
    const contacts = this.createRecipientOptions(contactRequest.data.results, query);

    console.log(contacts);

    return contacts;
  }

  async getDocument(documentId, recipient = '') {
    return axios.get(`/api/integrations/documents/${documentId}/send/?recipient=${recipient}`);
  }

  async getCustomVariable(variable, isPublic = false) {
    return axios.get(`/api/messaging/email/template-variables/?name=${variable}&public=${isPublic}`);
  }

  createRecipientLabel = (emailAddress, name = null) => {
    if (name) {
      return `${name} <${emailAddress}>`;
    }

    return emailAddress;
  }

  createRecipientOptions = (contacts, query = '') => {
    // TODO: This shouldn't be needed in the live version,
    // since we'll filter it out when querying.
    contacts = contacts.filter(contact => contact.emailAddresses.length > 0);

    const options = [];

    contacts.forEach(contact => {
      const containsDomain = contact.emailAddresses.some(emailAddress => {
        const emailDomain = emailAddress.emailAddress.split('@').slice(-1)[0];
        return emailDomain === query;
      });

      contact.emailAddresses.forEach(emailAddress => {
        const emailDomain = emailAddress.emailAddress.split('@').slice(-1)[0];

        // Filter contact's email addresses if we're searching with whole domain.
        if ((containsDomain && emailDomain !== query) || !emailAddress.isActive) {
          return;
        }

        const label = this.createRecipientLabel(emailAddress.emailAddress, contact.fullName);
        const contactCopy = Object.assign({}, contact);

        let accounts = [];

        if (contact.accounts.length > 0) {
          accounts = contact.accounts.filter(account => {
            // TODO: This check shouldn't be needed in the live version.
            if (account.domains) {
              // Check if any of the domains contain the email's domain.
              return account.domains.some(domain => domain.includes(emailDomain));
            } else {
              return [];
            }
          });

          if (accounts.length === 0) {
            accounts = contact.accounts;
          }

          // TODO: Temporary disable, re-enable on live.
          // accounts = accounts.filter(account => account.isActive);

          if (accounts.length === 0) {
            // If isn't active at the filtered account(s),
            // don't show the email address at all.
            return;
          }
        }

        contactCopy.accounts = accounts;
        contactCopy.emailAddress = emailAddress.emailAddress;

        const contactData = {
          label,
          value: contactCopy,
        }

        options.push(contactData);
      });
    });

    return options;
  }

  handleEmailAccountChange = emailAccount => {
    const user = this.state.user;

    user.currentEmailAddress = emailAccount ? emailAccount.value.emailAddress : null;

    this.setState({ emailAccount, user });
  }

  handleRecipientChange = recipients => {
    const newState = { recipients };

    if (recipients.length === 1) {
      const contact = recipients[0];
      newState.contact = contact;

      if (contact.value.accounts && contact.value.accounts.length === 1) {
        newState.account = contact.value.accounts[0];
      } else {
        newState.account = null;
      }
    } else if (recipients.length === 0) {
      newState.contact = null;
      newState.account = null;
    }

    this.setState(newState);

    setTimeout(() => this.scanTemplate());
  }

  handleAdditionalRecipients = (recipients, bcc = false) => {
    if (bcc) {
      this.setState({ recipientsBcc: recipients });
    } else {
      this.setState({ recipientsCc: recipients });
    }
  }

  handleSubjectChange = event => {
    this.setState({ subject: event.target.value })
  }

  handleTemplateChange = template => {
    let loadTemplate = true;

    // Check if a template has been loaded already.

    if (template) {
      let typedText = '';
      if (this.state.currentTemplate) {
        // Create a HTMLDocument from the given HTML string.
        const parser = new DOMParser();
        const currentDocument = parser.parseFromString(this.state.currentTemplate, 'text/html');
        const document = parser.parseFromString(this.refs.editor.getHtml(), 'text/html');
        // Get the root element of the document.
        const templateContent = currentDocument.body.innerHTML;
        const documentContent = document.body.innerHTML;

        // Create a character diff between the loaded template's HTML and the actual current HTML.
        const diff = JsDiff.diffWords(templateContent, documentContent);

        diff.forEach(part => {
          // Get all text that was changed/added.
          if (part.added) {
            typedText += part.value;
          }
        });

        if (typedText.indexOf('>') === 0) {
          // When there's a line break a bracket from the previous element is seen as a diff.
          // So just replace it if it's part of the diff.
          typedText = typedText.substr(1);
        }

        if (typedText.lastIndexOf('</') === (typedText.length - 2)) {
          // Same goes for any line breaks at the end.
          typedText = typedText.substr(0, typedText.length - 2);
        }
      }

      if (loadTemplate) {
        const { bodyHtml, subject, customVariables } = template.value;
        // TODO: Implement check to see if the message is a reply.
        // const subject = this.props.messageType === NEW_MESSAGE ? template.value.subject : this.state.message.subject;

        this.setState({ subject, template });
        this.loadTemplate(bodyHtml, subject, customVariables, typedText);
      }
    } else {
      this.setState({
        template: null,
        subject: ''
      });

      // TODO: This needs some more checks to prevent completely clearing the editor.
      this.refs.editor.setHtml('');
    }
  }

  scanTemplate = () => {
    const currentHtml = this.refs.editor.getHtml();

    // Create a HTMLDocument from the given HTML string.
    const parser = new DOMParser();
    const parsed = parser.parseFromString(currentHtml, 'text/html');
    // Get the root element of the document.
    const container = parsed.documentElement;

    const links = container.querySelectorAll('a');
    const specialVariableRegex = /{{ ([a-z]+\.[a-z_]+) }}/g;
    const { specialElements } = this.state;

    // Certain elements need to be processed differently.
    Array.from(links).forEach(link => {
      const { key } = link.dataset;

      if (specialElements.hasOwnProperty(key)) {
        const originalHtml = specialElements[key];

        const newHtml = originalHtml.replace(specialVariableRegex, (match, p1) => {
          const value = this.getValueForVariable(p1) || `{{ ${p1} }}`;

          return value;
        });

        link.outerHTML = newHtml;

        specialElements[key] = originalHtml;
      }
    });

    this.setState({ specialElements });

    // Get all the template variables.
    const variables = container.querySelectorAll('[data-variable]');

    Array.from(variables).forEach(variable => {
      // Convert back to a variable if the value has been cleared (e.g. recipient removed).
      variable.innerHTML = this.getValueForVariable(variable.dataset.variable) || `[[ ${variable.dataset.variable} ]]`;
    })

    this.refs.editor.setHtml(container.outerHTML);
  }

  loadTemplate = (html, subject = '', customVariables = [], typedText = '') => {
    const currentHtml = html || this.refs.editor.getHtml();
    const specialElements = {};

    // Regex to find variables which need special processing (e.g. variables in links).
    const specialVariableRegex = /{{ ?([a-z]+\.[a-z_]+) ?}}/g;

    // Create a HTMLDocument from the given HTML string.
    const parser = new DOMParser();
    const parsed = parser.parseFromString(currentHtml, 'text/html');
    // Get the root element of the document.
    const container = parsed.documentElement;

    const links = container.querySelectorAll('a');

    Array.from(links).forEach(link => {
      let addLink = false;

      // Generate some random string to clean up the keys of the special elements object.
      const key = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

      // Add our randomly generated key to the link's data attributes.
      link.dataset.key = key;

      // Replace all square brackets with normal ones.
      // This is because not every element can contain our special variable span.
      // This "original" HTML will be stored so it can be parsed again later.
      const originalHtml = link.outerHTML.replace(VARIABLE_REGEX, (match, p1) => `{{ ${p1} }}`);

      const newHtml = originalHtml.replace(specialVariableRegex, (match, p1) => {
        const value = this.getValueForVariable(p1) || `{{ ${p1} }}`;

        // Only store data for links which contain template variables.
        addLink = true;

        return value;
      });

      if (addLink) {
        link.outerHTML = newHtml;
        specialElements[key] = originalHtml;
      }
    });

    // Save the special elements so their data can be used later.
    this.setState({ specialElements });

    if (!TYPED_TEXT_REGEX.test(newHtml) && typedText) {
      container.innerHTML += typedText;
    }

    let newHtml = container.outerHTML;

    customVariables.forEach(variable => {
      // Replace any custom variables before we scan for regular template variables.
      const customVariableRegex = new RegExp(`\\[\\[ ?(custom\.${variable.variable}) ?\\]\\]`, 'g');

      newHtml = newHtml.replace(customVariableRegex, match => variable.text);
    });

    // Replace typed text variable with actual text (or leave empty).
    newHtml = newHtml.replace('[[ template.typed_text ]]', typedText);

    // Replace all regular template variables.
    newHtml = newHtml.replace(VARIABLE_REGEX, (match, p1) => {
      // If no value is found we leave the template variable so we can attempt to fill it in later.
      const value = this.getValueForVariable(p1) || match;

      return `<span data-variable="${p1}">${value}</span>`;
    });

    if (subject) {
      const newSubject = subject.replace(VARIABLE_REGEX, (match, p1) => {
        // If no value is found we leave the template variable so we can attempt to fill it in later.
        const value = this.getValueForVariable(p1) || match;

        return value;
      });

      this.setState({ subject: newSubject });
    }

    this.refs.editor.setHtml(newHtml);

    // The editor stores the HTML a bit differently than it's created.
    // To ensure we always have the correct format (for comparisons) we retrieve the HTML
    // instead of storing the newly creating HTML.
    this.setState({ currentTemplate:  this.refs.editor.getHtml() });
  }

  getValueForVariable = cleanedVariable => {
    let [model, field] = cleanedVariable.split('.');
    let value = null;

    const modelObject = this.state[model];

    if (modelObject) {
      // Convert our found variable to camelCase.
      field = convertKey(field);

      value = modelObject.hasOwnProperty('value') ? modelObject.value[field] : modelObject[field];
    }

    return value;
  };

  checkRecipientValidity = () => {
    const { recipients, recipientsCc, recipientsBcc } = this.state;

    // Check if any recipient has been filled in.
    const hasAnyRecipient = recipients.length > 0 || recipientsCc.length > 0 || recipientsBcc.length > 0;

    if (!hasAnyRecipient) {
      // TODO: This should just show an error.
      return false;
    }

    const allRecipients = recipients.concat(recipientsCc).concat(recipientsBcc);

    const allValid = allRecipients.every(recipient => {
      return EMAIL_REGEX.test(recipient.value.emailAddress);
    });

    if (!allValid) {
      return false;
    }

    return true;
  }

  validateEmailAddress = option => {
    return EMAIL_REGEX.test(option.label);
  }

  createRecipient = (option, type) => {
    const recipients = this.state[type];

    recipients.push({ value: option.value, label: option.value });

    this.setState({ [type]: recipients });
  }

  handleSubmit = () => {
    const { subject, files } = this.state;

    const recipientsValid = this.checkRecipientValidity();

    if (!recipientsValid) {
      // Don't submit and show errors.
      return;
    }

    if (!subject) {
      // Warn user that no subject has been entered.
      return;
    }

    // TODO: Temporary, this should be handled in some generic request setting.
    const crsf = document.cookie.match(new RegExp('csrftoken=([^;]+)'))[1];

    const recipients = this.state.recipients.map(recipient => ({ name: recipient.value.fullName, email_address: recipient.value.emailAddress }));

    const container = document.createElement('div');

    container.innerHTML = this.refs.editor.getHtml();

    // Get all the template variables.
    const variables = container.querySelectorAll('[data-variable]');

    let unparsedVariables = 0;

    Array.from(variables).forEach(variable => {
      // Check all variables if they've been parsed.
      let hasMatch = VARIABLE_REGEX.test(variable.innerHTML);

      if (hasMatch) {
        unparsedVariables += 1;
      } else {
        // Clean the variable spans so the email doesn't contain unneeded HTML.
        variable.outerHTML = variable.innerHTML;
      }
    });

    if (unparsedVariables > 0) {
      // Warn the user about any unparsed variables.
      // The user can then choose to fill in the variables anyway or
      // remove the unparsed variables (automatic action).
      // TODO: Actually implement the above.
      alert('Unparsed variables');
      return;
    }

    // TODO: Obviously remove.
    return;

    const bodyHtml = container.innerHTML;

    axios.post('/api/messaging/email/email/send_test/', {
      subject,
      account: this.state.emailAccount.value.id,
      body_html: bodyHtml,
      received_by: recipients
    }, {
        headers: { 'X-CSRFToken': crsf },
      }).then(response => {
        if (response.status === 201) {
          // Redirect back to the email list if we're mailing from the actual email compose.
          window.location = '/#/email'
        }
      });
  }

  optionRenderer = option => {
    if (option.value.hasOwnProperty('emailAddress')) {
      const contact = option.value;
      let accounts = '';

      if (contact.accounts && contact.accounts.length) {
        accounts = ` (${contact.accounts.map(account => account.name).join(', ')})`;
      }

      return (
        <div>
          <div>{contact.fullName} {accounts}</div>
          <div className="text-muted">{contact.emailAddress}</div>
        </div>
      );
    } else {
      // Render differently for option creation.
      return (
        <div className={option.className}>
          {option.label}
        </div>
      )
    }
  }

  render() {
    const { fixed } = this.props;
    const className = fixed ? 'editor fixed' : 'editor';
    const recipientProps = {
      styles,
      multi: true,
      loadOptions: throttle(this.getRecipients, 250),
      optionRenderer: this.optionRenderer,
      isValidNewOption: this.validateEmailAddress,
      className: 'editor-select-input'
    }

    return (
      <div className={className}>
        <div>
          {fixed && <div className="editor-header">Compose email</div>}

          <div className="editor-input-group">
            <label>From</label>

            <Select
              name="emailAccount"
              value={this.state.emailAccount}
              onChange={this.handleEmailAccountChange}
              options={this.state.emailAccounts}
              searchable={false}
              className="editor-select-input"
              styles={styles}
            />
          </div>

          <div className="editor-input-group">
            <label>To</label>

            <AsyncCreatable
              name="recipients"
              value={this.state.recipients}
              onChange={this.handleRecipientChange}
              onNewOptionClick={option => this.createRecipient(option, 'recipients')}
              { ...recipientProps }
            />

            {!this.state.showCcInput && <button className="hl-primary-btn no-border" onClick={() => this.setState({ showCcInput: true })}>CC</button>}
            {!this.state.showBccInput && <button className="hl-primary-btn no-border" onClick={() => this.setState({ showBccInput: true })}>BCC</button>}
          </div>

          {this.state.showCcInput &&
            <div className="editor-input-group">
              <label>CC</label>

              <AsyncCreatable
                name="recipientsCc"
                value={this.state.recipientsCc}
                onChange={this.handleAdditionalRecipients}
                onNewOptionClick={option => this.createRecipient(option, 'recipientsCc')}
                { ...recipientProps }
              />

              {this.state.showCcInput &&
                <button className="hl-primary-btn no-border" onClick={() => this.setState({ showCcInput: false })}>
                  <i className="fa fa-times" />
                </button>
              }
            </div>
          }

          {this.state.showBccInput &&
            <div className="editor-input-group">
              <label>BCC</label>

              <AsyncCreatable
                name="recipientsBcc"
                value={this.state.recipientsBcc}
                onChange={recipients => this.handleAdditionalRecipients(recipients, true)}
                onNewOptionClick={option => this.createRecipient(option, 'recipientsBcc')}
                { ...recipientProps }
              />

              {this.state.showBccInput &&
                <button className="hl-primary-btn no-border" onClick={() => this.setState({ showBccInput: false })}>
                  <i className="fa fa-times" />
                </button>
              }
            </div>
          }

          <div className="editor-input-group">
            <label>Template</label>

            <Select
              name="template"
              value={this.state.template}
              onChange={this.handleTemplateChange}
              options={this.state.templates}
              placeholder="Select a template"
              className="editor-select-input"
              styles={styles}
            />
          </div>

          <div className="editor-input-group">
            <label>Subject</label>

            <input
              type="text"
              className="editor-subject"
              value={this.state.subject}
              onChange={this.handleSubjectChange}
              placeholder="Subject"
            />
          </div>

          <LilyEditor ref="editor" codeViewCallback={html => this.loadTemplate(html)} maxHeight={this.props.maxHeight} modalOpen={this.state.modalOpen} />
        </div>

        <div className="editor-form-actions">
          <button className="hl-primary-btn-green no-margin" onClick={this.handleSubmit}><i className="fa fa-check" /> Send</button>

          <div className="separator"></div>

          <button className="hl-primary-btn" onClick={() => this.setState({ modalOpen: true })}><i className="lilicon hl-paperclip-icon" /> Add attachment</button>
          <button className="hl-primary-btn discard-button"><i className="lilicon hl-trashcan-icon" /> Discard</button>
        </div>
      </div>
    );
  }
}

angular
  .module('app.email.directives', [])
  .component('emailEditor', react2angular(EmailEditor, ['loadDefaultTemplate', 'maxHeight', 'recipients', 'emailMessage', 'fixed', 'documentId']))
