import React, { Component } from 'react';

import FroalaEditor from 'react-froala-wysiwyg';

import { MAX_FILE_SIZE } from './constants';

const Uppy = require('uppy/lib/core');
const XHRUpload = require('uppy/lib/plugins/XHRUpload');

const uppy = Uppy({
  restrictions: {
    maxFileSize: MAX_FILE_SIZE
  },
});

uppy.use(XHRUpload, {
  endpoint: '/api/messaging/email/upload'
})

uppy.run();

const DashboardModal = require('uppy/lib/react/DashboardModal');

class LilyEditor extends Component {
  constructor(props) {
    super(props);

    $.FroalaEditor.DefineIcon('uppy', {NAME: 'paperclip'});
    $.FroalaEditor.RegisterCommand('uppy', {
      title: 'Add attachment',
      focus: false,
      undo: false,
      refreshAfterCallback: false,
      callback: () => {
        this.setState({ modalOpen: true });
      }
    });

    // Configuration for the Froala Editor.
    this.config = {
      toolbarButtons: [
        'bold', 'italic', 'underline', 'fontSize', 'paragraphFormat', 'color',
        'align', 'clearFormatting', '|', 'insertLink', 'insertImage', 'html'
      ],
      spellcheck: false,
      fullPage: true,
      iframeStyle: 'body {font-family: Roboto, sans-serif; font-size: 14px;} body table td {border: 0 !important;}', // TODO: TEMPORARY STYLING
      events: {
        'froalaEditor.commands.after': this.handleCommandAfter,
        'froalaEditor.initialized': (e, editor) => this.setState({ editor })
      },
      pluginsEnabled: [
        'align', 'codeBeautifier', 'codeView', 'colors', 'draggable', 'embedly', 'entities', 'file',
        'fontSize', 'fullscreen', 'image', 'imageManager', 'inlineStyle', 'lineBreaker', 'link',
        'lists', 'paragraphFormat', 'paragraphStyle', 'quote', 'save', 'url', 'video', 'wordPaste'
      ],
      // TODO: Should be calculated instead of being hard coded and based on another property.
      toolbarStickyOffset: this.props.maxHeight ? 0 : 144,
      codeBeautifierOptions: {
        indent_char: ' ',
        indent_size: 4,
      },
      heightMin: 150,
      heightMax: this.props.maxHeight
      // saveURL: '/api/messaging/email/email/save_draft/',
      // saveParams: {
      //   subject: 'test'
      // }
    }

    this.state = {
      files: []
    }
  }

  static getDerivedStateFromProps = nextProps => ({ modalOpen: nextProps.modalOpen });

  setHtml = html => {
    this.state.editor.html.set(html);
  }

  getHtml = () => {
    return this.state.editor.html.get();
  }

  handleCommandAfter = (e, editor, cmd, param1, param2) => {
    if (cmd === 'html') {
      const isActive = editor.codeView.isActive();

      if (!isActive) {
        this.props.codeViewCallback(editor.html.get());
      }
    }
  }

  removeAttachment = file => {
    // Copy the files array.
    const { files } = uppy.getState();
    // Remove the file.
    delete files[file];

    uppy.setState({ files });
  }

  handleClose = () => {
    this.setState({ modalOpen: false });
  }

  bytesToSize = bytes => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return 'n/a';

    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10);

    if (i === 0) return `${bytes} ${sizes[i]}`;
    return `${(bytes / (1024 ** i)).toFixed(1)} ${sizes[i]}`;
  }

  render() {
    const { files } = uppy.getState();
    const { dropzoneActive } = this.state;

    return (
      <div>
        <DashboardModal
          uppy={uppy}
          closeModalOnClickOutside
          hideUploadButton
          showProgressDetails
          open={this.state.modalOpen}
          onRequestClose={this.handleClose}
        />

        <FroalaEditor
          tag="textarea"
          config={this.config}
        />

        {Object.keys(files).length > 0 &&
          <div className="editor-attachments">
            {
              Object.keys(files).map(key => {
                const file = files[key];

                return (
                  <div className="editor-attachment" key={file.name}>
                    <strong>
                      <div className="editor-attachment-name">{file.name}</div>
                      <div className="editor-attachment-size display-inline-block m-l-5">({this.bytesToSize(file.size)})</div>
                    </strong>
                    <button className="hl-primary-btn-smll no-border pull-right" onClick={() => this.removeAttachment(file.id)}>
                      <i className="lilicon hl-close-icon"></i>
                    </button>
                  </div>
                )
              })
            }
          </div>
        }
      </div>
    );
  }
}

export default LilyEditor;
