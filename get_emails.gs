function getGmailEmails(){
    var query = 'Вкусвилл before:2025/05/29';  // Modify this line as needed
    Logger.log("Current query: " + query);  // Log the current query to ensure it's being updated
    var threads = GmailApp.search(query);
    
    Logger.log("Number of threads found: " + threads.length);  // Log the number of threads found

    for(var i = 0; i < threads.length; i++){
        var messages = threads[i].getMessages();
        var msgCount = threads[i].getMessageCount();
        for (var j = 0; j < messages.length; j++){
            var message = messages[j];
            Logger.log("Processing email with subject: " + message.getSubject());  // Log each email's subject
            if (message.isInInbox()){
                extractDetails(message, msgCount);
            }
        }
    }
}

function extractDetails(message, msgCount){
    var spreadSheetId='19nGwGfKfV5-N72oVjE55JP3822xrviEUPU16G0m38pM';
    var sheetname = "vkusvill";
    var ss = SpreadsheetApp.openById(spreadSheetId);
    var sheet = ss.getSheetByName(sheetname);
    var dateTime = Utilities.formatDate(message.getDate(), "GMT", "dd-MM-yyyy HH:mm:ss");
    var subjectText = message.getSubject();
    var fromSend = message.getFrom();
    var toSend = message.getTo();
    var bodyContent = message.getPlainBody();
    sheet.appendRow([dateTime, msgCount, fromSend, toSend, subjectText, bodyContent]);
}

function onOpen(e) {
    SpreadsheetApp.getUi()
    .createMenu('Click to Fetch Emails')
    .addItem('Get Email', 'getGmailEmails')
    .addToUi();
}