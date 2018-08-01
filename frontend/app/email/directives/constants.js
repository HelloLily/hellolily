// Maximum file size allowed per attachment.
export const MAX_FILE_SIZE = 20 * 1024 * 1024;

// Regex to find normal variables.
export const VARIABLE_REGEX = /\[\[ ?([a-z]+\.[a-z_]+) ?]]/g;

// Separate regex for the typed_text variable.
export const TYPED_TEXT_REGEX = /\[\[ template\.typed_text \]\]/;

// Regex to detect if an email address is valid.
export const EMAIL_REGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

// Message types.
export const NEW_MESSAGE = 0;
export const DRAFT_MESSAGE = 1;
export const REPLY_MESSAGE = 2;
export const REPLY_ALL_MESSAGE = 3;
export const FORWARD_MESSAGE = 4;

/* eslint-disable */
export const SELECT_STYLES = {
  control: base => ({
    ...base,
    background: '#fff',
    minHeight: '30px',
    height: '34px',
    borderColor: '#e1e6ef'
  }),
  valueContainer: base => ({
    ...base,
    padding: '0 8px'
  }),
  input: base => ({
    ...base,
    paddingTop: '0',
    paddingBottom: '0',
    margin: '0 2px'
  }),
  dropdownIndicator: base => ({
    ...base,
    padding: '4px'
  }),
  option: base => ({
    ...base,
    padding: '6px 12px'
  }),
  menu: base => ({
    ...base,
    zIndex: '10'
  }),
  menuList: base => ({
    ...base,
    paddingTop: '0',
    paddingBottom: '0'
  }),
  multiValueLabel: base => ({
    ...base,
    lineHeight: '24px',
    padding: '0 4px'
  }),
  multiValueRemove: base => ({
    ...base,
    cursor: 'pointer'
  }),
  placeholder: base => ({
    ...base,
    color: '#b5b5b5'
  })
};

/* eslint-enable */
