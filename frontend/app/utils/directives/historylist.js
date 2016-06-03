angular.module('app.utils.directives').directive('historyList', HistoryListDirective);

HistoryListDirective.$inject = ['$filter', '$http', '$q', '$state', '$uibModal', 'EmailAccount',
    'Note', 'NoteDetail', 'Case', 'Deal', 'EmailDetail', 'User', 'HLGravatar', 'HLUtils'];
function HistoryListDirective($filter, $http, $q, $state, $uibModal, EmailAccount,
                              Note, NoteDetail, Case, Deal, EmailDetail, User, HLGravatar, HLUtils) {
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
        templateUrl: 'utils/directives/historylist.html',
        link: function(scope, element, attrs) {
            var page = 0;
            var pageSize = 50;

            scope.history = {};
            scope.history.list = [];
            scope.history.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases', visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false},
            };
            scope.history.activeFilter = '';
            scope.history.showMoreText = 'Show more';
            scope.history.loadMore = loadMore;
            scope.history.reloadHistory = reloadHistory;
            scope.history.addNote = addNote;
            scope.history.editNote = editNote;
            scope.history.pinNote = pinNote;
            scope.history.removeFromList = removeFromList;
            scope.history.filterType = filterType;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                HLUtils.blockUI('#historyListBlockTarget', true);
                // Somehow calling autosize on page content load does not work
                // in the historylist.
                autosize($('textarea'));
                loadMore();
            }

            function filterType(value) {
                var key;
                var selectedCount;

                scope.history.activeFilter = value;
                // Loop through the months to hide the monthname when there
                // aren't any items in that month that are shown due to
                // the filter that is being selected.
                for (key in scope.history.list.nonPinned) {
                    selectedCount = $filter('filter')(scope.history.list.nonPinned[key].items, {historyType: value}).length;
                    scope.history.list.nonPinned[key].isVisible = !!selectedCount;
                }
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchHistory(obj);
                    });
                } else {
                    _fetchHistory(scope.object);
                }
            }

            function reloadHistory() {
                page -= 1;
                loadMore();
            }

            function _fetchHistory(obj) {
                var history = [];
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
                var i;
                var filterquery;
                var currentObject = obj;
                var contentType = scope.target;

                if (scope.dateStart && scope.dateEnd) {
                    dateQuery = ' AND modified:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                    emailDateQuery = 'sent_date:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                }

                page += 1;

                filterquery = '(content_type:' + contentType + ' AND object_id:' + currentObject.id + ')';

                if (contentType === 'account' && currentObject.contact) {
                    // Show all notes of contacts linked to the account.
                    for (i = 0; i < currentObject.contact.length; i++) {
                        filterquery += ' OR (content_type:contact AND object_id:' + currentObject.contact[i] + ')';
                    }
                }

                if (scope.extraObject) {
                    filterquery += ' OR (content_type:' + scope.extraObject.target + ' AND object_id:' + scope.extraObject.object.id + ')';
                }

                filterquery = '(' + filterquery + ')';

                notePromise = NoteDetail.query({filterquery: filterquery + dateQuery, size: requestLength}).$promise;

                promises.push(notePromise);  // Add promise to list of all promises for later handling

                notePromise.then(function(results) {
                    results.forEach(function(note) {
                        // Get user for notes to show profile picture correctly.
                        User.get({id: note.author.id}, function(userObject) {
                            note.author = userObject;
                        });

                        // Set notes shown property to true to have toggled open as default.
                        if (note.is_pinned) {
                            note.shown = true;
                        }

                        // If it's a contact's note, add extra attribute to the note
                        // so we can identify it in the template
                        if (scope.target === 'account' && note.content_type === 'contact') {
                            note.showContact = true;
                        }

                        history.push(note);
                    });
                });

                if (scope.extraObject) {
                    currentObject = scope.extraObject.object;
                    contentType = scope.extraObject.target;
                }

                // We don't have to fetch extra objects for the case or deal
                // history list. So continue if we have an extra object or if
                // we're dealing with something else than a case or deal.
                if (contentType !== 'case' && contentType !== 'deal') {
                    filterquery = contentType + '.id:' + currentObject.id;

                    casePromise = Case.query({filterquery: filterquery + dateQuery, size: 100}).$promise;

                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(response) {
                        response.objects.forEach(function(caseItem) {
                            // Get user object for the assigned to user.
                            if (caseItem.assigned_to) {
                                User.get({id: caseItem.assigned_to.id}, function(userObject) {
                                    caseItem.assigned_to = userObject;
                                });
                            }

                            if (caseItem.created_by) {
                                // Get user object for the created by user.
                                User.get({id: caseItem.created_by.id}, function(userObject) {
                                    caseItem.created_by = userObject;
                                });
                            }

                            caseItem.historyType = 'case';

                            history.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 15})
                                .$promise.then(function(notes) {
                                    angular.forEach(notes, function(note) {
                                        // Get user for notes to show profile picture correctly.
                                        User.get({id: note.author.id}, function(author) {
                                            note.author = author;
                                        });
                                    });

                                    caseItem.notes = notes;
                                });
                        });
                    });

                    dealPromise = Deal.query({filterquery: filterquery + dateQuery, size: requestLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.objects.forEach(function(deal) {
                            if (deal.assigned_to) {
                                // Get user object for the assigned to user.
                                User.get({id: deal.assigned_to.id}, function(userObject) {
                                    deal.assigned_to = userObject;
                                });
                            }

                            if (deal.created_by) {
                                // Get user object to show profile picture correctly.
                                User.get({id: deal.created_by.id}, function(userObject) {
                                    deal.created_by = userObject;
                                });
                            }

                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5,
                            }).$promise.then(function(notes) {
                                angular.forEach(notes, function(note) {
                                    // Get user for notes to show profile picture correctly.
                                    User.get({id: note.author.id}, function(author) {
                                        note.author = author;
                                    });
                                });

                                deal.notes = notes;
                            });

                            history.push(deal);
                        });
                    });

                    tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise);

                    if (contentType === 'account') {
                        emailPromise = EmailDetail.query({account_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.query({contact_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    }

                    promises.push(emailPromise);

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0].results;
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            email.gravatar = HLGravatar.getGravatar(email.sender_email);

                            tenantEmailAccountList.forEach(function(emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });

                            history.push(email);
                        });
                    });
                }

                // Get all history types and add them to a common history.
                $q.all(promises).then(function() {
                    var orderedHistoryList = {pinned: [], nonPinned: {}, totalItems: history.length};

                    // To properly sort the history list we need to compare dates
                    // because email doesn't have the modified key we decided
                    // to add an extra key called historySortDate which the list
                    // uses to sort properly. We add the sent_date of email to the
                    // object, and the modified date for the other types.
                    for (i = 0; i < history.length; i++) {
                        if (history[i].historyType === 'email') {
                            history[i].historySortDate = history[i].sent_date;
                        } else {
                            history[i].historySortDate = history[i].modified;
                        }
                    }

                    $filter('orderBy')(history, 'historySortDate', true).forEach(function(item) {
                        var date = '';
                        var key = '';
                        var parentObjectId = scope.parentObject ? scope.parentObject.id : null;

                        scope.history.types[item.historyType].visible = true;

                        if (item.is_pinned) {
                            orderedHistoryList.pinned.push(item);
                        } else {
                            // Exclude the current item from the history list.
                            if (item.id !== scope.object.id && item.id !== parentObjectId) {
                                if (item.hasOwnProperty('modified')) {
                                    date = item.modified;
                                } else {
                                    date = item.sent_date;
                                }

                                key = moment(date).year() + '-' + (moment(date).month() + 1);

                                if (!orderedHistoryList.nonPinned.hasOwnProperty(key)) {
                                    orderedHistoryList.nonPinned[key] = {isVisible: true, items: []};
                                }

                                if (scope.target === 'case' && item.historyType === 'note' && item.content_type === 'case') {
                                    item.shown = true;
                                }

                                orderedHistoryList.nonPinned[key].items.push(item);
                            } else {
                                orderedHistoryList.totalItems -= 1;
                            }
                        }
                    });

                    // Get first key in the nonPinned list to target the first
                    // item in the history items to set the property to shown.
                    if (scope.target !== 'case' && Object.keys(orderedHistoryList.nonPinned).length) {
                        orderedHistoryList.nonPinned[Object.keys(orderedHistoryList.nonPinned)[0]].items[0].shown = true;
                    }

                    scope.history.list = orderedHistoryList;

                    HLUtils.unblockUI('#historyListBlockTarget');
                });
            }

            function addNote(note, form) {
                note.content_type = scope.object.content_type.id;
                note.object_id = scope.object.id;

                Note.save(note, function() {
                    // Success.
                    scope.note.content = '';
                    toastr.success('I\'ve created the note for you!', 'Done');
                    reloadHistory();
                }, function(response) {
                    // Error.
                    HLForms.setErrors(form, response.data);
                    toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                });
            }

            function editNote(note) {
                var modalInstance = $uibModal.open({
                    templateUrl: 'utils/controllers/note_edit.html',
                    controller: 'EditNoteModalController',
                    controllerAs: 'vm',
                    bindToController: true,
                    size: 'lg',
                    resolve: {
                        note: function() {
                            return Note.get({id: note.id}).$promise;
                        },
                    },
                });

                modalInstance.result.then(function() {
                    reloadHistory();
                });
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
                    index = scope.history.list.pinned.indexOf(item);
                    scope.history.list.pinned.splice(index, 1);
                } else {
                    index = scope.history.list.nonPinned[year + '-' + month].items.indexOf(item);
                    scope.history.list.nonPinned[year + '-' + month].items.splice(index, 1);
                }

                // We might be deleting the last object of a certain month.
                // Check if there are still items and hide the block if needed.
                if (!scope.history.list.nonPinned[year + '-' + month].items.length) {
                    scope.history.list.nonPinned[year + '-' + month].isVisible = false;
                }

                scope.$apply();
            }
        },
    };
}
