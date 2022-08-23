from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt, cstr, nowdate, comma_and
from frappe import throw, msgprint, _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from erpnext.accounts.utils import get_fiscal_year

@frappe.whitelist()
def make_deferred_revenue_settlement_journal_entry(company,revenue_account, deferred_revenue_account, posting_date=None, party_type=None, party=None, cost_center=None,
							project=None,save=True, submit=True):
		if not deferred_revenue_account:
			msgprint("Please set deferred revenue account")
			return

		if not revenue_account:
			msgprint("Please set revenue account")
			return

		amount = get_balance_on(account=deferred_revenue_account,project=project)
		if amount >= 0:
			msgprint("There is no credit balance on the deferred revenue account to be settled")
			return
		else:
			amount = abs(amount)

		jv = frappe.new_doc("Journal Entry")
		jv.posting_date = posting_date or nowdate()
		jv.company = company
		jv.user_remark = "Settle Deferred Revenue for Project" + project
		jv.multi_currency = 0
		jv.project = project
		jv.set("accounts", [
			{
				"account": deferred_revenue_account,
				"project": project,
				"debit_in_account_currency": amount
			}, {
				"account": revenue_account,
				"project": project,
				"credit_in_account_currency": amount
			}
		])
		if save or submit:
			jv.insert(ignore_permissions=True)

			if submit:
				jv.submit()

		message = """<a href="#Form/Journal Entry/%s" target="_blank">%s</a>""" % (jv.name, jv.name)
		msgprint(_("Journal Entry {0} created").format(comma_and(message)))
		#message = _("Journal Entry {0} created").format(comma_and(message))

		return message

@frappe.whitelist()
def make_unbilled_revenue_settlement_journal_entry(company,sales_order,wip_account, unbilled_revenue_account, posting_date=None, party_type=None, party=None, cost_center=None,
							project=None,percent_complete=0.0,save=True, submit=True):

		percent_complete = float(percent_complete)
		if not wip_account:
			msgprint("Please set WIP account")
			return

		if not unbilled_revenue_account:
			msgprint("Please set unbilled revenue account")
			return
		so_doc = frappe.get_doc('Sales Order', sales_order)
		wip_amount = get_balance_on(account=wip_account,project=project)
		so_amount = flt(so_doc.base_net_total)
		so_billed_amount = so_amount * flt(so_doc.per_billed) / 100
		so_unbilled_amount = (so_amount * percent_complete / 100) - so_billed_amount - wip_amount

		if so_unbilled_amount<=0:
			msgprint("there is no unbilled amount")
			return
		else:
			amount = abs(so_unbilled_amount)

		jv = frappe.new_doc("Journal Entry")
		jv.posting_date = posting_date or nowdate()
		jv.company = company
		jv.user_remark = "Settle unbilled Revenue for Project" + project
		jv.multi_currency = 0
		jv.project = project
		jv.set("accounts", [
			{
				"account": wip_account,
				"project": project,
				"debit_in_account_currency": amount
			}, {
				"account": unbilled_revenue_account,
				"project": project,
				"credit_in_account_currency": amount
			}
		])
		if save or submit:
			jv.insert(ignore_permissions=True)

			if submit:
				jv.submit()

		message = """<a href="#Form/Journal Entry/%s" target="_blank">%s</a>""" % (jv.name, jv.name)
		msgprint(_("Journal Entry {0} created").format(comma_and(message)))
		#message = _("Journal Entry {0} created").format(comma_and(message))

		return message

@frappe.whitelist()
def make_close_the_wip_account_journal_entry(company, wip_account, unbilled_revenue_account, posting_date=None, party_type=None, party=None, cost_center=None,
							project=None,save=True, submit=True):
		if not wip_account:
			msgprint("Please set WIP account")
			return

		if not unbilled_revenue_account:
			msgprint("Please set unbilled revenue account")
			return

		amount = get_balance_on(account=wip_account,project=project)
		if amount <= 0:
			msgprint("There is no credit balance on the deferred revenue account to be settled")
			return
		else:
			amount = abs(amount)

		jv = frappe.new_doc("Journal Entry")
		jv.posting_date = posting_date or nowdate()
		jv.company = company
		jv.user_remark = "Settle Deferred Revenue for Project" + project
		jv.multi_currency = 0
		jv.project = project
		jv.set("accounts", [
			{
				"account": unbilled_revenue_account,
				"project": project,
				"debit_in_account_currency": amount
			}, {
				"account": wip_account,
				"project": project,
				"credit_in_account_currency": amount
			}
		])
		if save or submit:
			jv.insert(ignore_permissions=True)

			if submit:
				jv.submit()

		message = """<a href="#Form/journal-entry/%s" target="_blank">%s</a>""" % (jv.name, jv.name)
		msgprint(_("Journal Entry {0} created").format(comma_and(message)))
		#message = _("Journal Entry {0} created").format(comma_and(message))

		return message


@frappe.whitelist()
def get_balance_on(
	account=None,
	date=None,
	party_type=None,
	party=None,
	company=None,
	in_account_currency=True,
	cost_center=None,
	project=None,
	ignore_account_permission=False,
):
	if not account and frappe.form_dict.get("account"):
		account = frappe.form_dict.get("account")
	if not date and frappe.form_dict.get("date"):
		date = frappe.form_dict.get("date")
	if not party_type and frappe.form_dict.get("party_type"):
		party_type = frappe.form_dict.get("party_type")
	if not party and frappe.form_dict.get("party"):
		party = frappe.form_dict.get("party")
	if not cost_center and frappe.form_dict.get("cost_center"):
		cost_center = frappe.form_dict.get("cost_center")
	if not project and frappe.form_dict.get("project"):
		project = frappe.form_dict.get("project")

	cond = ["is_cancelled=0"]
	if date:
		cond.append("posting_date <= %s" % frappe.db.escape(cstr(date)))
	else:
		# get balance of all entries that exist
		date = nowdate()

	if account:
		acc = frappe.get_doc("Account", account)

	try:
		year_start_date = get_fiscal_year(date, company=company, verbose=0)[1]
	except FiscalYearError:
		if getdate(date) > getdate(nowdate()):
			# if fiscal year not found and the date is greater than today
			# get fiscal year for today's date and its corresponding year start date
			year_start_date = get_fiscal_year(nowdate(), verbose=1)[1]
		else:
			# this indicates that it is a date older than any existing fiscal year.
			# hence, assuming balance as 0.0
			return 0.0

	if account:
		report_type = acc.report_type
	else:
		report_type = ""

	if cost_center and report_type == "Profit and Loss":
		cc = frappe.get_doc("Cost Center", cost_center)
		if cc.is_group:
			cond.append(
				""" exists (
				select 1 from `tabCost Center` cc where cc.name = gle.cost_center
				and cc.lft >= %s and cc.rgt <= %s
			)"""
				% (cc.lft, cc.rgt)
			)

		else:
			cond.append("""gle.cost_center = %s """ % (frappe.db.escape(cost_center, percent=False),))

	if project:
		cond.append("""gle.project = %s """ % (frappe.db.escape(project, percent=False),))

	if account:

		if not (frappe.flags.ignore_account_permission or ignore_account_permission):
			acc.check_permission("read")

		if report_type == "Profit and Loss":
			# for pl accounts, get balance within a fiscal year
			cond.append(
				"posting_date >= '%s' and voucher_type != 'Period Closing Voucher'" % year_start_date
			)
		# different filter for group and ledger - improved performance
		if acc.is_group:
			cond.append(
				"""exists (
				select name from `tabAccount` ac where ac.name = gle.account
				and ac.lft >= %s and ac.rgt <= %s
			)"""
				% (acc.lft, acc.rgt)
			)

			# If group and currency same as company,
			# always return balance based on debit and credit in company currency
			if acc.account_currency == frappe.get_cached_value("Company", acc.company, "default_currency"):
				in_account_currency = False
		else:
			cond.append("""gle.account = %s """ % (frappe.db.escape(account, percent=False),))

	if party_type and party:
		cond.append(
			"""gle.party_type = %s and gle.party = %s """
			% (frappe.db.escape(party_type), frappe.db.escape(party, percent=False))
		)

	if company:
		cond.append("""gle.company = %s """ % (frappe.db.escape(company, percent=False)))

	if account or (party_type and party):
		if in_account_currency:
			select_field = "sum(debit_in_account_currency) - sum(credit_in_account_currency)"
		else:
			select_field = "sum(debit) - sum(credit)"
		bal = frappe.db.sql(
			"""
			SELECT {0}
			FROM `tabGL Entry` gle
			WHERE {1}""".format(
				select_field, " and ".join(cond)
			)
		)[0][0]

		# if bal is None, return 0
		return flt(bal)


# def get_data():
# 	return {
# 		"fieldname": "project",
# 		"transactions": [
# 			{"label": _("Journal Entry"), "items": ["Journal Entry"]},
# 		],
# 	}
