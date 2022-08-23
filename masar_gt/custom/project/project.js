frappe.ui.form.on("Project", "refresh", function(frm) {
    frm.add_custom_button(__("Deferred Revenue Settlement"), function() {

      if (frm.doc.revenue == null || "" ) {
        frappe.msgprint("Please Set Revenue Account")
        return}

      if (frm.doc.deferred_revenue == null || "" ) {
        frappe.msgprint("Please Set Deferred Revenue Account")
        return}

      frappe.call({
    		method: "masar_gt.custom.project.project.make_deferred_revenue_settlement_journal_entry",
    		args: { company: frm.doc.company,
                revenue_account: frm.doc.revenue,
                deferred_revenue_account: frm.doc.deferred_revenue,
                project: frm.doc.name},
    	         });

          }, __("Manage"));
});


frappe.ui.form.on("Project", "refresh", function(frm) {
    frm.add_custom_button(__("Unbilled Revenue Settlement"), function() {

      if (frm.doc.wip_clients == null || "" ) {
        frappe.msgprint("Please Set WIP - Clients Account")
        return}

      if (frm.doc.unbilled_revenue == null || "" ) {
        frappe.msgprint("Please Set Unbilled Revenue Account")
        return}

      frappe.call({
		method: "masar_gt.custom.project.project.make_unbilled_revenue_settlement_journal_entry",
		args: { company: frm.doc.company,
            sales_order: frm.doc.sales_order,
            wip_account: frm.doc.wip_clients,
            unbilled_revenue_account: frm.doc.unbilled_revenue,
            project: frm.doc.name,
            percent_complete: frm.doc.percent_complete},
	         });

      }, __("Manage"));
});

frappe.ui.form.on("Project", "refresh", function(frm) {
    frm.add_custom_button(__("Close WIP Account"), function() {

      if (frm.doc.wip_clients == null || "" ) {
        frappe.msgprint("Please Set WIP - Clients Account")
        return}

      if (frm.doc.unbilled_revenue == null || "" ) {
        frappe.msgprint("Please Set Unbilled Revenue Account")
        return}
      
      frappe.call({
		method: "masar_gt.custom.project.project.make_close_the_wip_account_journal_entry",
		args: { company: frm.doc.company,
            wip_account: frm.doc.wip_clients,
            unbilled_revenue_account: frm.doc.unbilled_revenue,
            project: frm.doc.name},
	         });

      }, __("Manage"));
});
