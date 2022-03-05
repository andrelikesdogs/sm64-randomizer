let BASE_URL = "https://mayro.surf.garbage";

if (location.hostname == "localhost" || location.hostname == "127.0.0.1") {
  BASE_URL = "http://localhost:5000";
}

$(document).ready(() => {
  const tryGA = (action, opts) => {
    console.log("Logging Event: " + action);
    console.log(opts);
    try {
      gtag("event", action, opts);
    } catch (err) {
      console.warn("Could not save GA Event - probably blocked");
    }
  };
  const $fields = [];
  $.each(configurableParams, (_, field) => {
    const fieldName = field.name;
    const categoryName = field.category;
    $targetCategory = $(`#category-${categoryName}`);
    if (!$targetCategory.length) {
      throw new Error(`Category does not exist: ${categoryName}`);
    }

    if (fieldName == "seed") {
      field.default = Math.round(1e8 + Math.random() * 1e12).toString();
    }

    $field = $("<div />");
    $field.addClass("field");
    // console.log(field.disabled)

    const isDisabled = field.disabled != null;
    if (isDisabled) {
      $field.addClass("disabled");

      if (field.disabled !== true) {
        $field.addClass(field.disabled); // reason
      }
    }

    $input = $("<input />");
    $input.prop("disabled", isDisabled);

    fieldId = `#form-${fieldName}`;

    $input.attr("id", fieldId);
    $input.attr("name", fieldName);
    $input.prop("disabled", isDisabled);

    $label = $("<label />");
    $label.text(field.label);

    if (field.help) {
      $tooltipButton = $("<button />");
      $tooltipButton.attr("type", "button");
      $tooltipButton.addClass("help");

      $tooltipContent = $("<div />");
      $tooltipContent.text(field.help);
      $tooltipContent.addClass("tooltip-content");
      $tooltipContent.appendTo($tooltipButton);

      $label.append(" ").append($tooltipButton);
    }

    let fieldDefault = undefined;
    if (typeof field.default == "object") {
      if (field.default.WEB != null) {
        fieldDefault = field.default.WEB;
      }
    } else if (field.default && field.default.length > 0) {
      fieldDefault = field.default;
    }

    switch (field.type) {
      case "checkbox": {
        $input.attr("type", "checkbox");
        $input.prop("checked", fieldDefault);

        $field.append($input);
        $field.append($("<label />").attr("for", fieldId).text("Toggle"));
        $field.append(" ");
        $field.append($label);
        break;
      }
      case "select": {
        $input = $("<select />");
        $input.prop("disabled", isDisabled);
        $input.attr("name", fieldName);

        $.each(field.options, (_, { value, label }) => {
          $input.append($("<option />").attr("value", value).text(label));
        });

        $input.val(fieldDefault || field.values[Object.keys(field.options)[0]]);
        $field.append($label);
        $field.append($input);
        break;
      }
      case "text": {
        $input.attr("type", "text");
        $input.val(fieldDefault);

        $field.append($label);
        $field.append($input);
        break;
      }
      default: {
        console.warn("Invalid Field Type! Not adding Field");
        break;
      }
    }
    $fields.push($input);
    $field.addClass(`field--type--${field.type}`);
    $targetCategory.append($field);
  });

  let dataBlob;
  const $generatorForm = $('form[name="generator"]');

  // setup dropzone
  $targetInputField = $('input[type="file"]');
  $targetInputField.attr("name", "fake-upload");
  $fieldContainer = $targetInputField.closest(".field");
  $realUpload = $('input[name="hidden_upload"]');
  $realUpload.attr("name", "input_rom");

  $fileInputWrapped = $("<div />");
  $fileInputWrapped.addClass("file-upload-wrapper");
  $fieldContainer.children().first().wrapInner($fileInputWrapped);

  $fileInputStyled = $("<div />");
  $fileInputStyled.addClass("like-button").addClass("secondary");
  $fileInputStyled.text("Select your ROM-File");
  $fileInputStyled.insertAfter($targetInputField);

  $queueGenerationButton = $("#queue-generation");
  const changeEndianness = (string) => {
    const result = [];
    let len = string.length - 2;
    while (len >= 0) {
      result.push(string.substr(len, 2));
      len -= 2;
    }
    return result.join("");
  };

  let internalName;
  const validateROM = (arrayBuffer) => {
    const header = arrayBuffer.slice(0, 0x40);

    const endian_bytes = [header[0], header[1]];
    let endianess = "unknown";

    if (endian_bytes.toString() == [0x80, 0x37].toString()) {
      endianess = "big";
    } else if (endian_bytes.toString() == [0x37, 0x80].toString()) {
      endianess = "mixed";
    } else if (endian_bytes.toString() == [0x40, 0x12].toString()) {
      endianess = "little";
    } else {
      //console.log(endian_bytes.toString())
      throw new Error(
        "Sorry, that doesn't seem like a ROM (Invalid byte-order bytes)"
      );
    }
    //console.log(header.slice(0x18, 0x3B))

    internalName = String.fromCharCode.apply(
      null,
      new Uint8Array(header.slice(0x18, 0x3b))
    );

    if (endianess == "little") {
      internalName = changeEndianness(internalName);
    }

    internalName = internalName.replace(/[^A-Za-z0-9 ]+/g, "").trim();

    if (internalName != "SUPER MARIO 64") {
      console.log(internalName);
      //throw new Error('invalid internal name - must be a SM64 ROM')
    }

    return arrayBuffer;
  };

  const tryCompress = async (file) => {
    const zipBlob = await new Promise((callback) => {
      const zipWriter = zip.createWriter(
        new zip.BlobWriter(),
        (writerInstance) => {
          writerInstance.add(file.name, new zip.BlobReader(file), () => {
            writerInstance.close(callback);
          });
        }
      );
    });

    return zipBlob;
  };

  let fileNameSelected;
  const validateInput = async (files) => {
    if (files.length > 1) {
      throw new Error("Please only upload one file at a time");
    }

    if (!files) {
      console.warn("No file selected");
      return;
    }

    fileNameSelected = files[0].name;

    binaryData = await new Promise((resolve, reject) => {
      const fileReader = new FileReader();
      fileReader.onload = (e) => {
        binaryData = new Uint8Array(fileReader.result);
        resolve(binaryData);
      };
      fileReader.onerror = (e) => {
        reject(e);
      };
      fileReader.readAsArrayBuffer(files[0]);
    });

    return validateROM(binaryData);
  };

  const updateInputStatus = (status, message) => {
    // clear everything
    $targetInputField.prop("disabled", false);
    $message = $(".message").text("");
    $message.addClass(status);
    $message.text(message);

    const canChange = status === "success" || status === "error";
    $targetInputField.prop("disabled", !canChange);
  };

  let tracking_active = false;
  let tracking_interval = null;
  let used_seed = null;
  const activateTrackingMode = (upload_ticket) => {
    if (!tracking_active) {
      tracking_active = true;
      tracking_interval = setInterval(() => {
        $.ajax({
          type: "GET",
          url: BASE_URL + "/status/" + upload_ticket,
          success: (data) => {
            console.log(data);
            if (data.status == "SUCCESS") {
              clearInterval(tracking_interval);
              tracking_active = false;

              $downloadLink = $("<a />");
              $downloadLink.addClass("download-rom");
              $downloadLink.attr(
                "href",
                BASE_URL + "/download/" + upload_ticket
              );
              const fileNameParts = fileNameSelected.split(".");
              const fileExt = fileNameParts[fileNameParts.length - 1];
              $downloadLink.attr(
                "download",
                'SM64Randomizer (Seed "' + used_seed + '").' + fileExt
              );
              $downloadLink.text("Download your ROM!");

              if ($queueGenerationButton.next().hasClass("download-rom")) {
                $queueGenerationButton.next().remove();
              }
              $($queueGenerationButton).after($downloadLink);
              $downloadLink.get(0).click();

              // queue-generation-message
              $queueGenerationButton
                .children("span")
                .text("Queue for generation");
              $queueGenerationButton.prop("disabled", false);
              $queueGenerationButton.removeClass("indefinite");

              tryGA("rom_received", {
                event_category: "ROM Received",
                label: "User received a ROM",
              });

              return;
            } else if (data.status == "ERROR") {
              clearInterval(tracking_interval);
              tracking_active = false;

              tryGA("rom_failure_resp", {
                event_category: "ROM Received",
                label:
                  "ROM Receive failed: " +
                  (data && data.message != null
                    ? data.message
                    : "(Unknown Error)"),
              });

              alert(
                data.message ||
                  "Sorry! An unknown error occured. Please try again later or ask for support on our Discord."
              );
              $queueGenerationButton
                .children("span")
                .text("Queue for generation");
              $queueGenerationButton.prop("disabled", false);
              $queueGenerationButton.removeClass("indefinite");
              return;
            } else if (data.status == "PROCESSING") {
              $queueGenerationButton
                .children("span")
                .text("Generating your ROM...");
            } else if (data.status == "PENDING") {
              if (data.position == 0) {
                $queueGenerationButton.children("span").text("You're next!");
              } else {
                $queueGenerationButton
                  .children("span")
                  .text(
                    "Currently waiting on " +
                      data.position +
                      " others ahead in the queue."
                  );
              }
            }
          },
          error: (xhr, errMessage) => {
            clearInterval(tracking_interval);
            tracking_active = false;

            tryGA("rom_failure_xhr", {
              event_category: "ROM Received",
              label:
                "ROM Receive failed: " +
                (errMessage != null ? errMessage : "(Unknown Error)"),
            });

            alert(
              "Unfortunately the server returned an invalid response. Please try again later"
            );

            $queueGenerationButton
              .children("span")
              .text("Queue for generation");
            $queueGenerationButton.prop("disabled", false);
            $queueGenerationButton.removeClass("indefinite");
            return;
          },
        });
      }, 5000);
    }
  };

  $targetInputField.on("change", async function () {
    if (!this.files || !this.files[0]) {
      return;
    }

    dataBlob = null;
    updateInputStatus("pending");

    let blob;
    try {
      await validateInput(this.files);
      blob = this.files[0];
    } catch (err) {
      $fileInputStyled.text("Invalid Input");
      console.error(err);
      return updateInputStatus("error", err.message);
    }

    const might_be_romhack =
      internalName != "SUPER MARIO 64" &&
      internalName != "USEP RAMIR O46      N"; // lol

    let URL;
    let message = "";
    try {
      URL = window.webkitURL || window.mozURL || window.URL;
      updateInputStatus("load", "Compressing your ROM...");
      blob = await tryCompress(this.files[0]);
      dataBlob = blob;
      message = "Prepared your ROM for uploading!";
    } catch (err) {
      console.error(err);
      dataBlob = blob;
      message = "File prepared, but could not compress the data. Sorry!";
    }

    if (might_be_romhack) {
      updateInputStatus(
        "success",
        message + " (Your ROM was detected as a ROMHack)"
      );
      $fileInputStyled.text("✓ Valid ROM - Romhack");
    } else {
      updateInputStatus("success", message);
      $fileInputStyled.text("✓ Valid ROM");
    }

    $realUpload.val(URL.createObjectURL(blob));
  });

  $generatorForm.on("submit", (e) => {
    e.preventDefault();

    if (!$realUpload.val()) {
      alert("Please select a ROM that you want to randomize first!");
      return;
    }

    tryGA("upload_start", {
      event_category: "ROM Upload",
      label: "Started uploading a ROM",
    });
    const formDataBlob = new FormData(document.querySelector("form"));
    formDataBlob.delete("fake-upload");
    formDataBlob.set("input_rom", dataBlob, "input_rom.zip");

    used_seed = formDataBlob.get("seed");

    if ($queueGenerationButton.next().hasClass("download-rom")) {
      $queueGenerationButton.next().remove();
    }

    $queueGenerationButton.prop("disabled", true);
    $queueGenerationButton.children("span").text("Uploading...");

    $.ajax({
      type: "POST",
      url: BASE_URL,
      processData: false,
      contentType: false,
      data: formDataBlob,
      dataType: "json",
      success: (data) => {
        $queueGenerationButton.children("span").text("Waiting for queue...");
        $queueGenerationButton.addClass("indefinite");

        if (data.success) {
          tryGA("upload_finish", {
            event_category: "ROM Uploaded",
            label: "Completed an upload, waiting for queue",
          });
          activateTrackingMode(data.upload_ticket);
        } else {
          tryGA("upload_failed_resp", {
            event_category: "ROM Upload Failed",
            label:
              "Failed Uploading: " +
              (data && data.message != null ? data.message : "(Unknown Error)"),
          });
          console.error(data.message);
          $queueGenerationButton
            .children("span")
            .text("Sorry, an error occured. Please try again.");
          $queueGenerationButton.prop("disabled", false);
          $queueGenerationButton.removeClass("indefinite");
        }
      },
      error: (xhr, errMessage) => {
        tryGA("upload_failed_xhr", {
          event_category: "ROM Upload Failed",
          label:
            "Failed Uploading: " +
            (errMessage != null ? errMessage : "(Unknown Error)"),
        });
        $queueGenerationButton
          .children("span")
          .text("Sorry, an error occured. Please try again.");
        $queueGenerationButton.prop("disabled", false);
        $queueGenerationButton.removeClass("indefinite");
        $queueGenerationButton.children(".progress").css("width", "0%");
      },
      xhr: () => {
        const xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener("progress", (evt) => {
          var percentComplete = evt.loaded / evt.total;
          //console.log(percentComplete)
          $queueGenerationButton
            .children(".progress")
            .css("width", percentComplete * 100 + "%");
        });

        return xhr;
      },
    });
  });
});
