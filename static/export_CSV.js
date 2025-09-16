
//Export Button Handler
const exportBtn = document.querySelector('.btn-export')
if(exportBtn) {
   exportBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if(triggerExport()){
            exportCSV();
        }
        
   });
}



// Shared validation and export logic
function triggerExport(){
   
    const ipInput = document.querySelector('.seg');
    const subnetMask = document.querySelector('.cidr-seg');

    // Validate inputs. (?)is the optional chaining operator. It checks if ipInput is not null or undefined before calling
    if (!ipInput?.value.trim() || !subnetMask?.value.trim()) {
        alert('Please enter an IP address and subnet mask.');
        return false; // Validation failed
    }
    return true; // Validation passed
}



async function exportCSV(){
   try{
      
        const table = document.querySelector('table');
        const tableBody = table?.querySelector('tbody'); //?. is the optional chaining operator. It checks if table is not null or undefined before calling the querySelector

        if (!tableBody) {
            window.alert('No data found to export.');
            return;
        }

        //get column headers from table <thead>
        const tableHeaders = Array.from(table.querySelectorAll('thead th')) //Array.from() Converts the NodeList returned by querySelectorAll into a regular JavaScript array.

        //For each header cell (th), gets its text content and removes any leading/trailing whitespace.
        const headers = tableHeaders.map((header) => header.textContent.trim());

        //Read all rows 
        const rows = Array.from(tableBody.rows);

        // Prepare array of objects, each representing a row with header: value pairs
        const data = rows.map((row) => {
            const cells = Array.from(row.cells); //Cells represent the table data or information (td) 
            const tableData = {}; //Defining an object

            //Iterate over each cell and sets the property name to the corresponding headers using its index or set to default text at its index (e.g Column 1). Assigns the retrieved cell text content as the property value
            cells.forEach((cell, index) => {
                tableData[headers[index] || `Column ${index+1}`] = cell.textContent.trim();
            })

            return tableData;

        });




        //Create a response object and Sends subnet data as JSON in the request body
        //fetch JavaScript API for making HTTP requests
        const response = await fetch('/api/export_csv', {
          method: 'POST',
          headers: {'Content-Type' : 'application/json'},
          body: JSON.stringify({ data }) // Convert subnets JS object into JSON
        })

        //check if response status is OK (200 range)
        if(!response.ok){
          //await is used to pause the execution used inside asynchronous function
          const result = await response.json()
          alert(result.error || 'Error exporting data')
          return;
        }

        //Gets CSV as blob(file-like binary data)
        const blob = await response.blob();

        // Create a temporary URL that points to the blob data (browser memory reference)
        const url = window.URL.createObjectURL(blob)

        // Create a temporary invisible anchor (<a>) element
        const a = document.createElement('a')

        // Set the anchor's href attribute to our blob URL
        a.href = url

        // Set the suggested filename when downloaded
        a.download = "ExporedData.csv";

        // Append the anchor to the document body so we can click it
        document.body.appendChild(a);

        // Programmatically click the anchor which triggers the browser download
        a.click();

        document.body.removeChild(a);

    
    }
    catch(err){
    alert(`Export error: ${err.message}`)
  }
}



  