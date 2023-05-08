
//Alias query selector as $
const $ = (selector) => { return document.querySelector(selector) };
const $all = (selector) => { return document.querySelectorAll(selector) };

async function getFlaskComponent(url, target){
    const response = await fetch(url);
    response.text().then((html) => {
        $(target).innerHTML = html
    })
}

async function getCompanies(company_id=null) {
    //If there's no id just update the existing data
    company_id = (!company_id) ? $("#sidebar-company-details .header").dataset.companyId : company_id;
    const response = await fetch("/api/?id="+company_id);
    const jsonData = await response.json();
    const item = jsonData[0];
    $("#sidebar-company-details").innerHTML = `
        <p class="header" data-company-id="${company_id}">${item["name"]}</p>
        <p class="subheader">${item["street"]}. ???, ${item["state"]} ${item["zip"]}</p>
        <ul class="pills">
            <li id="company-size">${item["size"]} Employees</li>
            <li id="company-area">${item["area"]}</li>
            <li id="company-2year">Hire 2 Year?: ${item["hire2year"]}</li>
            <li id="company-intern">Internship? ${item["intern"]}</li>
        </ul>
    `;
  } 

async function getContacts(company_id=null) {
    //If there's no id just update the existing data
    company_id = (!company_id) ? $("#sidebar-company-details .header").dataset.companyId : company_id;
    const response = await fetch("/api/contacts?id="+company_id);
    const jsonData = await response.json();
    $("#sidebar-contact-details").innerHTML = '';
    jsonData.forEach((contact) => {
        $("#sidebar-contact-details").innerHTML += `
            <button class="sidebar-icon" id="sidebar_contact-edit" data-bs-toggle="modal" data-bs-target="#updateContactModal" data-contact_id="${contact['contact_id']}"></button>
            <p class="header">${contact['firstname']} ${contact['lastname']}</p>
            <p class="subheader">${contact['phone']}</p>
            <ul class="pills">
                <li>Department: ${contact['area']}</li>
                <li>Contact in Future: ${contact['can_contact_future']}</li>
                <textarea class="notes" readonly>${contact['notes']}</textarea>
            </ul>
        `;
    });
} 

async function getTech(company_id) {
    //If there's no id just update the existing data
    company_id = (!company_id) ? $("#sidebar-company-details .header").dataset.companyId : company_id;
    const response = await fetch("/api/tech?id="+company_id);
    const jsonData = await response.json();
    $("#sidebar-tech-details ol").innerHTML = `
        <div class="table-head">
            <li>Name</li>
            <li>Area</li>
            <li>Used Now</li>
            <li>Teach</li>
            <li>Top 3</li>
            <li>Continue</li>
            <li>Edit</li>
        </div>
    `;
    jsonData.forEach((tech) => {
        $("#sidebar-tech-details ol").innerHTML += `
        <div class="table-row">
            <li>${tech['tech_name']}</li>
            <li>${tech["tech_area"]}</li>
            <li>${tech["ct_usednow"]}</li>
            <li>${tech["ct_shouldteach"]}</li>
            <li>${tech["ct_topthree"]}</li>
            <li>${tech["ct_continue"]}</li>
            <li><button class="generic-icon editIcon" data-bs-toggle="modal" data-bs-target="#updateTechModal" data-ct_id="${tech['ct_id']}"></li>
        </div>
        `;
    });
} 


async function formSubmit(form, url, modalID, originalForm=null) {
    let request = await fetch(url, 
        { 
            method: "POST",
            body: new FormData(form)
        }
    );
    let response = request.text();
    //Reset Form
    if(!originalForm){
        getFlaskComponent(originalForm, `${modalID} .modal-body`)
    } 
    //Close Modal
    $(`${modalID} .modal-close`).click();
    //Update Data
    if(modalID != "#newCompanyModal"){
        getCompanies();
        getContacts();
        getTech();
    }
    return response;
}

function createCompanyCard(id, html){
    let newCard = document.createElement('div');
    newCard.classList = "infoBubble col companyCard";
    newCard.dataset.dbid = id.toString();
    newCard.innerHTML = html;
    return newCard;
}

function createNewCompanyNode(response){
    //Clone the last node
    response = JSON.parse(response);
    $(".infoBubble:last-of-type").insertAdjacentElement('afterend', createCompanyCard(response["id"], response["html"]));
    //Attach event listener
    $(".companyCard:last-of-type").addEventListener("click", () => {
        if(!$("#sidebar").classList.contains("opened")){
            $("#sidebar").classList.add("opened");
        }
        //Get the data and fill out the side bar
        getCompanies(this.dataset.dbid);
        getContacts(this.dataset.dbid);
        getTech(this.dataset.dbid);
    });
}

window.addEventListener("load", (event) => {

    //NEW COMPANY
    //Focus on first input box when the new company modal is opened.
    $('#newCompanyModal').addEventListener('shown.bs.modal', () => {
        $('#newCompanyModal input').focus()
    })

    //NEW COMPANY SUBMIT
    //Submit the form when the new company modal is submitted
    $("#newCompanyModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#newCompanyModal form"), "/submit_company", "#newCompanyModal", "/new_company_form").then((response) => {
            createNewCompanyNode(response);
        });
    });

    //NEW CONTACT
    //Focus on first input box when the new contact modal is opened.
    $('#newContactModal').addEventListener('shown.bs.modal', () => {
        let id = $("#sidebar-company-details .header").dataset.companyId;
        getFlaskComponent("/new_contact_form?id="+id, "#newContactModal .modal-body");
        $('#newContactModal input').focus()
    })
    //NEW CONTACT SUBMIT
    $("#newContactModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#newContactModal form"), "/submit_contact", "#newContactModal");
    });

    //NEW COMPANY TECH
    //Focus on first input box when the new tech modal is opened.
    $('#newCompanyTechModal').addEventListener('shown.bs.modal', () => {
        let id = $("#sidebar-company-details .header").dataset.companyId;
        getFlaskComponent("/new_company_tech_form?id="+id, "#newCompanyTechModal .modal-body");
        $('#newCompanyTechModal input').focus()
    })
    //NEW COMPANY TECH SUBMIT
    $("#newCompanyTechModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#newCompanyTechModal form"), "/submit_company_tech", "#newCompanyTechModal");
    });
    //NEW TECH
    //Focus on first input box when the new tech modal is opened.
    $('#newTechModal').addEventListener('shown.bs.modal', () => {
        getFlaskComponent("/new_tech_form", "#newTechModal .modal-body");
        $('#newTechModal input').focus()
    })
    //NEW TECH SUBMIT
    $("#newTechModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#newTechModal form"), "/submit_tech", "#newTechModal");
        location.reload();
    });
    //UPDATE TECH
    //Focus on first input box when the update tech modal is opened.
    $('#updateTechModal').addEventListener('shown.bs.modal', (e) => {
        let id = e.relatedTarget.dataset.ct_id;
        getFlaskComponent("/modify_company_tech?id="+id, "#updateTechModal .modal-body");
        $('#updateTechModal input').focus()
    })
    //UPDATE TECH SUBMIT
    //Submit the form when the update company modal is submitted
    $("#updateTechModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#updateTechModal form"), "/modified_ct", "#updateTechModal");
    });
    //Delete button
    $("#updateTechModal .modal-delete").addEventListener("click", () => {
        formSubmit($("#updateTechModal form"), "/delete_company_tech", "#updateTechModal");
    });

    //UPDATE COMPANY
    //Focus on first input box when the update company modal is opened.
    $('#updateCompanyModal').addEventListener('shown.bs.modal', () => {
        let id = $("#sidebar-company-details .header").dataset.companyId;
        getFlaskComponent("/update_company_form?id="+id, "#updateCompanyModal .modal-body");
        $('#updateCompanyModal input').focus()
    })

    //UPDATE COMPANY SUBMIT
    //Submit the form when the update company modal is submitted
    $("#updateCompanyModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#updateCompanyModal form"), "/modified_company", "#updateCompanyModal");
    });
    //Delete button
    /* $("#updateCompanyModal .modal-delete").addEventListener("click", () => {
        formSubmit($("#updateCompanyModal form"), "/delete_company", "#updateCompanyModal");
    }); */


    //UPDATE CONTACT
    //Focus on first input box when the update contact modal is opened.
    $('#updateContactModal').addEventListener('shown.bs.modal', (e) => {
        let id = e.relatedTarget.dataset.contact_id;
        console.log(id);
        //let id = $("#sidebar-company-details .header").dataset.companyId;
        getFlaskComponent("/modify_contact?id="+id, "#updateContactModal .modal-body");
        $('#updateContactModal input').focus()
    })

    //UPDATE CONTACT SUBMIT
    //Update contact modal submit
    $("#updateContactModal .modal-submit").addEventListener("click", () => {
        formSubmit($("#updateContactModal form"), "/modified_contact", "#updateContactModal");
    });
    //Delete button
    $("#updateContactModal .modal-delete").addEventListener("click", () => {
        formSubmit($("#updateContactModal form"), "/delete_contact", "#updateContactModal");
    });


    //Get the rendered html from the server for the new company form
    getFlaskComponent("/new_company_form", "#newCompanyModal .modal-body");
    
    //Side bar close button
    $("#sidebar_close").addEventListener("click", () => {
        if($("#sidebar").classList.contains("opened")){
            $("#sidebar").classList.remove("opened");
        }
    });

    $all(".companyCard").forEach((card) => {
        card.addEventListener("click", () => {
            if(!$("#sidebar").classList.contains("opened")){
                $("#sidebar").classList.add("opened");
            }
            //Get the data and fill out the side bar
            getCompanies(card.dataset.dbid);
            getContacts(card.dataset.dbid);
            getTech(card.dataset.dbid);
        });
    });

});