frappe.ui.form.on('Quotation', {
	 refresh: function(frm) {

	 }
});


frappe.ui.form.on("Quotation", {
    quotation_document_template: function(frm, cdt, cdn) {
			  show_alert(frm.doc.quotation_document_template, 5);
        frm.doc.quotation_documents = []
        frappe.call({
            method: "frappe.client.get",
            args: {
                name: frm.doc.quotation_document_template,
                doctype: "Quotation Document Template"
            },
            callback(r) {
                if (r.message) {
                    for (var row in r.message.required_documents) {
                        var child = frm.add_child("quotation_documents");
                        frappe.model.set_value(child.doctype, child.name, "document_code", r.message.required_documents[row].document_code);
                        frappe.model.set_value(child.doctype, child.name, "document_description", r.message.required_documents[row].document_description);
                        refresh_field("quotation_documents");
                    }

                }
            }

        })
    }
})



frappe.ui.form.on("Quotation", "before_submit", function(frm, cdt, cdn) {

   var child_doc = frm.doc.quotation_documents;
   for(var i in child_doc) {
		 if (child_doc[i].doc_attach == null){
			frappe.msgprint(child_doc[i].document_code);
			frappe.validated = false;
  	 }
	}
});
