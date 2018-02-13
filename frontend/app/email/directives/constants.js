// Maximum file size allowed per attachment.
export const MAX_FILE_SIZE = 20 * 1024 * 1024;

// Regex to find normal variables.
export const VARIABLE_REGEX = /\[\[ ?([a-z]+\.[a-z_]+) ?]]/g;

// Separate regex for the typed_text variable.
export const TYPED_TEXT_REGEX = /\[\[ template\.typed_text \]\]/;

// Regex to detect if an email address is valid.
export const EMAIL_REGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
