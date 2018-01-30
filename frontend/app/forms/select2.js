(function($, window, document) {
    window.HLSelect2 = {
        config: {
            tagInputs: 'input.tags',
            ajaxInputs: 'input.select2ajax',
            tagsAjaxClass: 'tags-ajax',
            ajaxPageLimit: 30,
            clearText: '-- Clear --',
        },

        init: function(config) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            // On initialize, setup select2
            self.setupSelect2();
            self.initListeners();
        },

        initListeners: function() {
            var self = this;
            // When modal is shown, lets instantiate the select2 in the modals
            $(document).on('shown.bs.modal', '.modal', function() {
                self.setupSelect2();
            });
        },

        setupSelect2: function() {
            // Setup select2 for non-ajaxified selects, ajaxified selects
            // are using hidden inputs.
            $('select').select2({
                // at least this many results are needed to enable the search field
                // (9 is the amount at which the user must scroll to see all items)
                minimumResultsForSearch: 9,
            });

            this.createTagInputs();
            this.createAjaxInputs();
        },

        createTagInputs: function() {
            var tags = [];
            var $this;

            // Setup tag inputs
            $(this.config.tagInputs).each(function() {
                if (!$(this).data().hasOwnProperty('select2')) {
                    $this = $(this);

                    if ($this.data('choices')) {
                        tags = $this.data('choices').split(',');
                    }

                    $this.select2({
                        tags: tags,
                        tokenSeparators: [','],
                        width: '100%',
                        createSearchChoice: function(term, data) { // eslint-disable-line consistent-return
                            if ($(data).filter(function() {
                                return this.text.localeCompare(term) === 0;
                            }).length === 0) {
                                return {
                                    id: term,
                                    text: term + ' (new tag)',
                                };
                            }
                        },
                    });
                }
            });
        },

        formatResult: function(result, container, query, escapeMarkup) {
            var resultRow = '';
            var nameMarkup = [];
            var emailMarkup = [];
            var markup = [];

            if (result.name && result.email_address) {
                window.Select2.util.markMatch(result.name, query.term, nameMarkup, escapeMarkup);
                window.Select2.util.markMatch(result.email_address, query.term, emailMarkup, escapeMarkup);

                let accounts = '';

                if (result.accounts && result.accounts.length) {
                    accounts = ` (${result.accounts.map(account => account.name).join(', ')})`;
                }

                resultRow =
                    '<div>' +
                    '<div>' + nameMarkup.join('') + accounts + '</div>' +
                    '<div class="text-muted">' + emailMarkup.join('') + '</div>' +
                    '</div>';
            } else {
                window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);

                resultRow =
                    '<div>' +
                    '<div>' + markup.join('') + '</div>' +
                    '</div>';
            }

            return resultRow;
        },

        createAjaxInputs: function() {
            // Setup inputs that needs remote link.
            var self = this;
            var cf = self.config;

            $(cf.ajaxInputs).each(function() {
                var options;
                var filterQuery;

                var $this = $(this);
                var _data = $this.data();

                if (_data.hasOwnProperty('tags')) {
                    _data.tags = true;
                }

                // _data.tags is a marker for AjaxSelect2Widget which indicates
                // that it expects multiple values as input.

                // Prevent Select2 from being initialized on elements that already have Select2.
                if (!_data.hasOwnProperty('select2')) {
                    options = {
                        formatResult: self.formatResult,
                        ajax: {
                            cache: true,
                            data: function(searchTerm, page) {
                                var termStripped;
                                var filters;

                                // Page is the one-based page number tracked by Select2.
                                var data = null;
                                var term;

                                if (searchTerm === '') {
                                    // Elasticsearch breaks when the term is empty, so just look for non-empty results.
                                    term = '*';
                                } else {
                                    // Otherwise escape the search term so special characters don't break Elasticsearch.
                                    term = '"' + searchTerm + '"';
                                }

                                if ($this.hasClass(cf.tagsAjaxClass) && !_data.tags) {
                                    // Search for contacts or accounts that match the search term and have an email address, and
                                    // where the contact belongs to one or more accounts, and are active at at least one account,
                                    // or contacts that don't belong to an account at all.
                                    filterQuery = '((_type:contacts_contact AND active_at:(*) AND (full_name:(' + term + ') OR email_addresses.email_address:(' + term + '))) ' +
                                        'OR (_type:contacts_contact AND NOT active_at:(*) AND NOT accounts:(*) AND (full_name:(' + term + ') OR email_addresses.email_address:(' + term + '))) ' +
                                        'OR (_type:accounts_account AND (full_name:(' + term + ') OR email_addresses.email_address:(' + term + ')))) ' +
                                        'AND email_addresses.email_address:*';

                                    data = {
                                        filterquery: filterQuery,
                                        size: cf.ajaxPageLimit, // page size
                                        page: (page - 1), // page number, zero-based
                                        sort: '-modified', // sort modified descending
                                    };

                                    cf.searchTerm = searchTerm;
                                } else {
                                    termStripped = term.trim();
                                    data = {
                                        filterquery: termStripped ? 'name:(' + termStripped + ')' : '', //search term
                                        size: cf.ajaxPageLimit, // page size
                                        page: (page - 1), // page number, zero-based
                                        sort: '-modified', // sort modified descending
                                    };
                                }

                                filters = $this.data('filter-on');

                                if (typeof filters !== 'undefined' && filters !== '') {
                                    filters.split(',').forEach(function(filter) {
                                        var filterVal;
                                        var filterName;

                                        if (filter.indexOf('id_') === 0) {
                                            filterVal = $('#' + filter).val();
                                            filterName = filter.substring(3);

                                            if (filterName.indexOf('case_quickbutton_') === 0) {
                                                filterName = filter.substring(20);
                                            } else if (filterName === 'account') {
                                                // This is a special case at the moment, in the future we might have
                                                // more cases like this.
                                                // But for now, just do this check
                                                filterName = 'accounts.id';
                                            }
                                            if (filterVal && filterVal > 0) {
                                                data.filterquery += ' ' + filterName + ':' + filterVal;
                                            }
                                        } else {
                                            data.type = filter;
                                        }
                                    });
                                }

                                return data;
                            },

                            results: function(data, page) {
                                if ($this.hasClass(cf.tagsAjaxClass) && !_data.tags) {
                                    const parsedData = [];

                                    const {searchTerm} = cf;

                                    data.hits.forEach(hit => {
                                        const containsDomain = hit.email_addresses.some(email => {
                                            const emailDomain = email.email_address.split('@').slice(-1)[0];
                                            return emailDomain === searchTerm;
                                        });

                                        // Only display contacts with an email address.
                                        hit.email_addresses.forEach(email => {
                                            const displayedName = hit.full_name || hit.name;
                                            const emailDomain = email.email_address.split('@').slice(-1)[0];

                                            // Filter contact's email addresses if we're searching with whole domain.
                                            if ((containsDomain && emailDomain !== searchTerm) || !email.is_active) {
                                                return;
                                            }

                                            // The text which is actually used in the application.
                                            const usedText = `"${displayedName}" <${email.email_address}>`;
                                            // The displayed text.
                                            const displayedText = `${displayedName} <${email.email_address}>`;

                                            let accounts = hit.accounts.filter(account => {
                                                // Check if any of the domains contain the email's domain.
                                                return account.domains.some(domain => domain.includes(emailDomain));
                                            });

                                            if (!accounts.length) {
                                                accounts = hit.accounts;
                                            }

                                            accounts = accounts.filter(account => account.is_active);

                                            if (accounts.length === 0) {
                                                // If isn't active at the filtered account(s),
                                                // don't show the email address at all.
                                                return;
                                            }

                                            // Select2 sends 'id' as the value, but we want to use the email.
                                            // So store the actual id (hit.id) under a different name.
                                            const contact = {
                                                accounts,
                                                id: usedText,
                                                text: displayedText,
                                                name: displayedName,
                                                email_address: email.email_address,
                                                object_id: hit.id,
                                            };

                                            parsedData.push(contact);
                                        });
                                    });

                                    // Array elements with empty text can't be added to select2,
                                    // so manually fill a new array.
                                    data.hits = parsedData;
                                } else {
                                    data.hits.forEach(hit => {
                                        hit.text = hit.name;
                                    });
                                }

                                // Add clear option, but not for multiple select2.
                                if ((page === 1 && !$this.hasClass(cf.tagsAjaxClass)) && !_data.tags) {
                                    data.hits.unshift({id: '', text: cf.clearText});
                                }

                                const more = (page * cf.ajaxPageLimit) < data.total;

                                return {
                                    results: data.hits,
                                    more: more,
                                };
                            },
                        },

                        initSelection: function(item, callback) {
                            var id = item.val();
                            var text = item.data('selected-text');
                            var data = {id: id, text: text};
                            callback(data);
                        },
                    };

                    if ($this.hasClass(cf.tagsAjaxClass)) {
                        options.tags = true;
                        options.tokenSeparators = [','];
                        // Create a new tag if there were no results
                        options.createSearchChoice = function(term, data) { // eslint-disable-line consistent-return
                            if ($(data).filter(function() {
                                return this.text.localeCompare(term) === 0;
                            }).length === 0) {
                                return {
                                    id: term,
                                    text: term,
                                };
                            }
                        };
                        // Prevent select2 dropdown from opening when pressing enter
                        options.openOnEnter = false;
                    }

                    // Set select2 to multiple.
                    if (_data.tags) {
                        options.tags = true;
                        options.multiple = true;
                    }

                    $this.select2(options);
                    // Set the initial form value from a JSON encoded data attribute called data-initial
                    if (_data.tags) {
                        $this.select2('data', _data.initial);
                    }
                }
            });
        },
    };
})(jQuery, window, document);
