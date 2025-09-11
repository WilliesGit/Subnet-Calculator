async function exportCSV(){
   try{
      const table_actions = document.querySelector('.table-actions');

      if(table_actions){
          const btn_export = document.querySelector('.btn-export')
          console.log("✅ Form submit handler triggered");

          const form = document.querySelector('.panel');

          //Getting the table's data rows
          const tableBody = document.querySelector('table tbody');

          if(!tableBody){
             // If table not found, show error to user
                window.alert('No data found to export.');
                return;
          }

          if(!form){
             // If table not found, show error to user
                window.alert('Fields cannot be empty');
                return;
          }

          //Defining an array list to store table data row
          const tableBodyData = [...tableBody.rows]

          //Defining object to store each table row
          const subnets = {};

          //Iterate over all rows in the table body
          tableBodyData.forEach((row, index)=>{
            // Each cell's text in a row represents a column
            subnets[index] = {
              network: row.cells[0].textContent, // Get text from 1st column
              broadcast: row.cells[1].textContent, // Get text from 2nd column
              first: row.cells[2].textContent, // Get text from 3rd column
              last: row.cells[3].textContent, // Get text from 2nd column


            };
          });

          //Create a response object and Sends subnet data as JSON in the request body
          //fetch JavaScript API for making HTTP requests
          const response = await fetch('/api/export_csv', {
            method: 'POST',
            headers: {'Content-Type' : 'application/json'},
            body: JSON.stringify({ subnets }) // Convert subnets JS object into JSON
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
          a.download = "Subnets.csv";

          // Append the anchor to the document body so we can click it
          document.body.appendChild(a);

          // Programmatically click the anchor which triggers the browser download
          a.click();

          document.body.removeChild(a);

      
      }
   }

   catch(err){
      alert(`Export error: ${err.message}`)
    }
}