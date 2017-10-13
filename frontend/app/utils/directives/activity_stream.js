angular.module('app.utils.directives').directive('activityStream', ActivityStreamDirective);

ActivityStreamDirective.$inject = ['$filter', '$q', '$state', 'Account', 'Case', 'Change', 'Contact', 'Deal',
    'EmailAccount', 'EmailDetail', 'HLGravatar', 'HLResource', 'HLUtils', 'HLForms', 'Note', 'NoteDetail', 'User'];
function ActivityStreamDirective($filter, $q, $state, Account, Case, Change, Contact, Deal, EmailAccount,
    EmailDetail, HLGravatar, HLResource, HLUtils, HLForms, Note, NoteDetail, User) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '=',
            dateStart: '=?',
            dateEnd: '=?',
            extraObject: '=?',
            parentObject: '=?',
        },
        templateUrl: 'utils/directives/activity_stream.html',
        link: function(scope, element, attrs) {
            const HOURS_BETWEEN_CHANGES = 1;
            const DATE_FORMAT = 'D MMM. YYYY';

            var page = 0;
            var pageSize = 50;

            scope.activity = {};
            scope.activity.list = [];
            scope.activity.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases', visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false},
                'call': {name: 'Calls', visible: false},
                'change': {name: 'Changes', visible: false},
            };
            scope.activity.activeFilter = '';
            scope.activity.showMoreText = 'Show more';
            scope.activity.changeLogMapping = {
                'phone_numbers': 'number',
                'email_addresses': 'email_address',
                'websites': 'website',
                'assigned_to_teams': 'name',
                'tags': 'name',
                'linkedin': 'username',
                'twitter': 'username',
                'accounts': 'name',
            };
            scope.activity.displayNameMapping = {
                'assigned_to_teams': 'Teams',
                'accounts': 'Works at',
            };
            scope.activity.mergeChanges = true;

            scope.activity.loadMore = loadMore;
            scope.activity.reloadActivity = reloadActivity;
            scope.activity.addNote = addNote;
            scope.activity.pinNote = pinNote;
            scope.activity.removeFromList = removeFromList;
            scope.activity.filterType = filterType;
            scope.activity.getValueRelated = getValueRelated;
            scope.activity.getChangeDisplayName = getChangeDisplayName;
            scope.activity.toggleMergeChanges = toggleMergeChanges;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                HLUtils.blockUI('#activityStreamBlockTarget', true);
                // Somehow calling autosize on page content load does not work
                // in the activity stream.
                autosize($('textarea'));
                loadMore();
            }

            function filterType(value) {
                var key;
                var selectedCount;

                scope.activity.activeFilter = value;
                // Loop through the months to hide the month name when there
                // aren't any items in that month that are shown due to
                // the filter that is being selected.
                for (key in scope.activity.list.nonPinned) {
                    selectedCount = $filter('filter')(scope.activity.list.nonPinned[key].items, {activityType: value}).length;
                    scope.activity.list.nonPinned[key].isVisible = !!selectedCount;
                }
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchActivity(obj);
                    });
                } else {
                    _fetchActivity(scope.object);
                }
            }

            function reloadActivity() {
                page -= 1;
                loadMore();
            }

            function _fetchActivity(obj) {
                var activity = [];
                var promises = [];
                var neededLength = (page + 1) * pageSize;
                var requestLength = neededLength + 1;
                var notePromise;
                var dateQuery = '';
                var emailDateQuery = '';
                var casePromise;
                var dealPromise;
                var tenantEmailAccountPromise;
                var emailPromise;
                let changePromise;
                var i;
                var filterquery;
                var currentObject = obj;
                var contentType = scope.target;
                let callPromise;
                let targetPlural = scope.target + 's';

                if (scope.dateStart && scope.dateEnd) {
                    dateQuery = ' AND modified:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                    emailDateQuery = 'sent_date:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                }

                page += 1;

                filterquery = '(content_type:' + contentType + ' AND object_id:' + currentObject.id + ')';

                if (contentType === 'account' && currentObject.contacts) {
                    // Show all notes of contacts linked to the account.
                    for (i = 0; i < currentObject.contacts.length; i++) {
                        filterquery += ' OR (content_type:contact AND object_id:' + currentObject.contacts[i].id + ')';
                    }
                }

                if (scope.extraObject) {
                    filterquery += ' OR (content_type:' + scope.extraObject.target + ' AND object_id:' + scope.extraObject.object.id + dateQuery + ')';
                }

                filterquery = '(' + filterquery + ')';

                notePromise = NoteDetail.query({filterquery: filterquery, size: requestLength}).$promise;

                // Add promise to list of all promises for later handling.
                promises.push(notePromise);

                notePromise.then(function(results) {
                    results.forEach(function(note) {
                        // Get user for notes to show profile picture correctly.
                        User.get({id: note.author.id, is_active: 'All'}, function(userObject) {
                            note.author = userObject;
                        });

                        // If it's a contact's note, add extra attribute to the note
                        // so we can identify it in the template.
                        if (scope.target === 'account' && note.content_type === 'contact') {
                            note.showContact = true;
                        }

                        activity.push(note);
                    });
                });

                changePromise = Change.query({id: currentObject.id, model: targetPlural}).$promise;

                promises.push(changePromise);  // Add promise to list of all promises for later handling

                changePromise.then(results => {
                    let changes = [];
                    let previousTime;
                    let futureTime;

                    if (scope.activity.mergeChanges) {
                        // Merge individual changes to a single change if they're within a certain time period.
                        results.objects.map((change, index) => {
                            let currentTime = moment(change.created);
                            let addNewChange = false;

                            if (index) {
                                let previousChange = changes[changes.length - 1];

                                if (previousChange.user.id === change.user.id) {
                                    if (currentTime.isBetween(previousTime, futureTime)) {
                                        change.data = Object.assign(previousChange.data, change.data);
                                        // Data was merged, so remove the previous entry and add the edited change.
                                        changes.pop();
                                    } else {
                                        addNewChange = true;
                                    }
                                } else {
                                    addNewChange = true;
                                }
                            } else {
                                addNewChange = true;
                            }

                            changes.push(change);

                            if (addNewChange) {
                                previousTime = currentTime;
                                futureTime = moment(currentTime).add(HOURS_BETWEEN_CHANGES, 'hours');
                            }
                        });
                    } else {
                        changes = results.objects;
                    }

                    changes.map(change => {
                        // Normal fields with a single change.
                        change.normal = {};
                        // Fields which can contain multiple values (e.g. phone numbers).
                        change.related = {};
                        // Store all changes keys.
                        change.changedKeys = [];

                        for (let key in change.data) {
                            if (Array.isArray(change.data[key].new)) {
                                change.related[key] = [];

                                let oldData = change.data[key].old;
                                let newData = change.data[key].new;

                                newData.map(newItem => {
                                    let changeItem = {};
                                    let oldItem;
                                    let field = getValueRelated(key);

                                    let found = oldData.some(oldDataItem => {
                                        oldItem = oldDataItem;
                                        return oldItem.hasOwnProperty('id') && oldItem.id === newItem.id;
                                    });

                                    if (found) {
                                        // Old item exists, but new item is deleted.
                                        if (newItem.hasOwnProperty('is_deleted')) {
                                            changeItem = {
                                                'old': oldItem[field] || oldItem,
                                                'new': null,
                                            };
                                        } else {
                                            // Both old and new item exist, so it's an edit.
                                            changeItem = {
                                                'old': oldItem[field] || oldItem,
                                                'new': newItem[field] || newItem,
                                            };
                                        }
                                    } else {
                                        // No old item, so it's an addition.
                                        changeItem = {
                                            'old': null,
                                            'new': newItem[field] || newItem,
                                        };
                                    }

                                    let displayName = getChangeDisplayName(key, true);

                                    change.related[key].push(changeItem);
                                    change.related[key].displayName = displayName;

                                    if (!change.changedKeys.includes(displayName)) {
                                        change.changedKeys.push(displayName);
                                    }
                                });
                            } else {
                                let data = change.data[key];
                                let oldDataEmpty = (data.old === undefined || data.old === '' || data.old === null);
                                let newDataEmpty = (data.new === undefined || data.new === '' || data.new === null);

                                if (!oldDataEmpty && !newDataEmpty) {
                                    data.changeType = 'edit';
                                } else if (!oldDataEmpty && newDataEmpty) {
                                    data.changeType = 'delete';
                                } else {
                                    data.changeType = 'add';
                                }

                                if (!oldDataEmpty) {
                                    let oldDate = moment(new Date(data.old.toString()));

                                    if (oldDate.isValid()) {
                                        data.old = oldDate.format(DATE_FORMAT);
                                    }
                                }

                                if (!newDataEmpty) {
                                    let newDate = moment(new Date(data.new.toString()));

                                    if (newDate.isValid()) {
                                        data.new = newDate.format(DATE_FORMAT);
                                    }
                                }

                                let displayName = getChangeDisplayName(key);

                                change.normal[key] = data;
                                change.normal[key].displayName = getChangeDisplayName(key);

                                if (!change.changedKeys.includes(displayName)) {
                                    change.changedKeys.push(displayName);
                                }
                            }
                        }

                        // Our data was put in other keys, so just remove the data key.
                        delete change.data;

                        change.relatedCount = Object.keys(change.related).length;

                        activity.push(change);
                    });
                });

                if (scope.extraObject) {
                    currentObject = scope.extraObject.object;
                    contentType = scope.extraObject.target;
                }

                // We don't have to fetch extra objects for the case or deal
                // activity list. So continue if we have an extra object or if
                // we're dealing with something else than a case or deal.
                if (contentType !== 'case' && contentType !== 'deal') {
                    filterquery = contentType + '.id:' + currentObject.id;

                    casePromise = Case.search({filterquery: filterquery + dateQuery, size: 100}).$promise;

                    // Add promise to list of all promises for later handling.
                    promises.push(casePromise);

                    casePromise.then(function(response) {
                        response.objects.forEach(function(caseItem) {
                            // Get user object for the assigned to user.
                            if (caseItem.assigned_to) {
                                User.get({id: caseItem.assigned_to.id, is_active: 'All'}, function(userObject) {
                                    caseItem.assigned_to = userObject;
                                });
                            }

                            if (caseItem.created_by) {
                                // Get user object for the created by user.
                                User.get({id: caseItem.created_by.id, is_active: 'All'}, function(userObject) {
                                    caseItem.created_by = userObject;
                                });
                            }

                            caseItem.activityType = 'case';

                            activity.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 15})
                                .$promise.then(function(notes) {
                                    angular.forEach(notes, function(note) {
                                        // Get user for notes to show profile picture correctly.
                                        User.get({id: note.author.id, is_active: 'All'}, function(author) {
                                            note.author = author;
                                        });
                                    });

                                    caseItem.notes = notes;
                                });
                        });
                    });

                    dealPromise = Deal.search({filterquery: filterquery + dateQuery, size: requestLength}).$promise;
                    // Add promise to list of all promises for later handling.
                    promises.push(dealPromise);

                    dealPromise.then(function(results) {
                        results.objects.forEach(function(deal) {
                            if (deal.assigned_to) {
                                // Get user object for the assigned to user.
                                User.get({id: deal.assigned_to.id, is_active: 'All'}, function(userObject) {
                                    deal.assigned_to = userObject;
                                });
                            }

                            if (deal.created_by) {
                                // Get user object to show profile picture correctly.
                                User.get({id: deal.created_by.id, is_active: 'All'}, function(userObject) {
                                    deal.created_by = userObject;
                                });
                            }

                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5,
                            }).$promise.then(function(notes) {
                                angular.forEach(notes, function(note) {
                                    // Get user for notes to show profile picture correctly.
                                    User.get({id: note.author.id, is_active: 'All'}, function(author) {
                                        note.author = author;
                                    });
                                });

                                deal.notes = notes;
                            });

                            activity.push(deal);
                        });
                    });

                    if (contentType === 'account') {
                        callPromise = Account.getCalls({id: currentObject.id}).$promise;
                    } else {
                        callPromise = Contact.getCalls({id: currentObject.id}).$promise;
                    }

                    // Add promise to list of all promises for later handling.
                    promises.push(callPromise);

                    callPromise.then(data => {
                        data.results.map(call => {
                            NoteDetail.query({filterquery: 'content_type:call AND object_id:' + call.id, size: 15})
                                .$promise.then(notes => {
                                    angular.forEach(notes, note => {
                                        // Get user for notes to show profile picture correctly.
                                        User.get({id: note.author.id, is_active: 'All'}, author => {
                                            note.author = author;
                                        });
                                    });

                                    call.notes = notes;
                                });

                            activity.push(call);
                        });
                    });

                    tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise);

                    if (contentType === 'account') {
                        emailPromise = EmailDetail.search({account_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.search({contact_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    }

                    promises.push(emailPromise);

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0].results;
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            User.search({filterquery: 'email:' + email.sender_email, is_active: 'All'}).$promise.then(function(userResults) {
                                if (userResults.objects[0]) {
                                    email.profile_picture = userResults.objects[0].profile_picture;
                                } else {
                                    email.profile_picture = HLGravatar.getGravatar(email.sender_email);
                                }
                            });

                            tenantEmailAccountList.forEach(function(emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });

                            activity.push(email);
                        });
                    });
                }

                // Get all activity types and add them to a common activity stream.
                $q.all(promises).then(function() {
                    var orderedActivityStream = {pinned: [], nonPinned: {}, totalItems: activity.length};

                    // To properly sort the activity list we need to compare dates
                    // because email doesn't have the modified key we decided
                    // to add an extra key called activitySortDate which the list
                    // uses to sort properly. We add the sent_date of email to the
                    // object, and the modified date for the other types.
                    for (i = 0; i < activity.length; i++) {
                        if (activity[i].activityType === 'email') {
                            activity[i].activitySortDate = activity[i].sent_date;
                        } else if (['note', 'change', 'call'].includes(activity[i].activityType)) {
                            // We want to sort certain objects on created date.
                            activity[i].activitySortDate = activity[i].date;
                        } else {
                            activity[i].activitySortDate = activity[i].modified;
                        }
                    }

                    $filter('orderBy')(activity, 'activitySortDate', true).forEach(item => {
                        var parentObjectId = scope.parentObject ? scope.parentObject.id : null;

                        scope.activity.types[item.activityType].visible = true;

                        if (item.is_pinned) {
                            orderedActivityStream.pinned.push(item);
                        } else {
                            // Exclude the current item from the activity list.
                            if (item.id !== scope.object.id && item.id !== parentObjectId) {
                                let date = item.activitySortDate;
                                let key = moment(date).year() + '-' + (moment(date).month() + 1);

                                if (!orderedActivityStream.nonPinned.hasOwnProperty(key)) {
                                    orderedActivityStream.nonPinned[key] = {isVisible: true, items: []};
                                }

                                item.shown = true;

                                orderedActivityStream.nonPinned[key].items.push(item);
                            } else {
                                orderedActivityStream.totalItems -= 1;
                            }
                        }
                    });

                    scope.activity.list = orderedActivityStream;

                    HLUtils.unblockUI('#activityStreamBlockTarget');
                });
            }

            function addNote(note, form) {
                if (note.content) {
                    note.content_type = scope.object.content_type.id;
                    note.object_id = scope.object.id;

                    Note.save(note, function() {
                        // Success.
                        scope.note.content = '';
                        toastr.success('I\'ve created the note for you!', 'Done');
                        reloadActivity();
                    }, function(response) {
                        // Error.
                        HLForms.setErrors(form, response.data);
                        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                    });
                }
            }

            function pinNote(note, isPinned) {
                Note.update({id: note.id}, {is_pinned: isPinned}, function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function removeFromList(item) {
                var month = moment(item.modified).format('M');
                var year = moment(item.modified).format('YYYY');
                var index;

                if (item.is_pinned) {
                    index = scope.activity.list.pinned.indexOf(item);
                    scope.activity.list.pinned.splice(index, 1);
                } else {
                    index = scope.activity.list.nonPinned[year + '-' + month].items.indexOf(item);
                    scope.activity.list.nonPinned[year + '-' + month].items.splice(index, 1);
                }

                // We might be deleting the last object of a certain month.
                // Check if there are still items and hide the block if needed.
                if (!scope.activity.list.nonPinned[year + '-' + month].items.length) {
                    scope.activity.list.nonPinned[year + '-' + month].isVisible = false;
                }

                scope.$apply();
            }

            function getValueRelated(field) {
                // Since every model has a different field which contains the value
                // we set up a mapping and retreive the proper field.
                return scope.activity.changeLogMapping[field];
            }

            function getChangeDisplayName(field, capitalize = false) {
                // For certain fields we don't want to show the field as it's named in the database.
                // So we set up a mapping and retrieve a nicer name.
                // Also cleans up underscores for all other fields.
                let displayName;

                if (scope.activity.displayNameMapping.hasOwnProperty(field)) {
                    displayName = scope.activity.displayNameMapping[field];
                } else {
                    // Replace underscore and uppercase first letter.
                    displayName = field.replace(/_/g, ' ');

                    if (capitalize) {
                        displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1);
                    }
                }

                return displayName;
            }

            function toggleMergeChanges() {
                scope.activity.mergeChanges = !scope.activity.mergeChanges;
                reloadActivity();
            }
        },
    };
}
