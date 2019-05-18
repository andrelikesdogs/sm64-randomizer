$(document).ready(() => {
  $.each(configurableParams, (_, field) => {
    const fieldName = field.name
    const categoryName = field.category
    $targetCategory = $(`#category-${categoryName}`)
    if (!$targetCategory.length) {
      throw new Error(`Category does not exist: ${categoryName}`)
    }
    
    $field = $('<div />')
    $field.addClass('field')
    
    $input = $('<input />')
    fieldId = `#form-${fieldName}`
    $input.attr('id', fieldId)

    $label = $('<label />')
    $label.text(field.label)

    if (field.help) {
      $tooltipButton = $('<button />')
      $tooltipButton.attr('type', 'button')
      $tooltipButton.addClass('help')

      $tooltipContent = $('<div />')
      $tooltipContent.text(field.help)
      $tooltipContent.addClass('tooltip-content')
      $tooltipContent.appendTo($tooltipButton)

      $label.append(' ').append($tooltipButton)
    }

    let fieldDefault = undefined
    if (typeof field.default == 'object') {
      if (field.default.WEB != null) {
        fieldDefault = field.default.WEB
      }
    } else if (field.default.length > 0) {
      fieldDefault = field.default
    }

    switch(field.type) {
      case 'checkbox': {
        $input.attr('type', 'checkbox')
        $input.prop('checked', fieldDefault)

        $field.append($input)
        $field.append($('<label />').attr('for', fieldId).text('Toggle'))
        $field.append(' ')
        $field.append($label)
        break
      }
      case 'select': {
        $input = $('<select />')

        $.each(field.options, (_, {value, label}) => {
          $input.append($('<option />').attr('value', value).text(label))
        })
        $input.val(fieldDefault || field.values[Object.keys(field.options)[0]])
        $field.append($label)
        $field.append($input)
        break
      }
      case 'text': {
        $input.attr('type', 'text')
        $input.val(fieldDefault)

        $field.append($label)
        $field.append($input)
        break
      }
      default: {
        console.warn('Invalid Field Type! Not adding Field')
        break
      }
    }
    $field.addClass(`field--type--${field.type}`)
    $targetCategory.append($field)
  })

  // setup dropzone
  $targetInputField = $('input[type="file"]')
  $targetInputField.attr('name', 'fake-upload')
  $fieldContainer = $targetInputField.closest('.field')
  $realUpload = $('input[name="hidden_upload"]')
  $realUpload.attr('name', 'input_rom')

  $fileInputWrapped = $('<div />')
  $fileInputWrapped.addClass('file-upload-wrapper')
  $fieldContainer.children().first().wrapInner($fileInputWrapped)

  $fileInputStyled = $('<div />')
  $fileInputStyled.addClass('like-button').addClass('secondary')
  $fileInputStyled.text('Select your ROM-File')
  $fileInputStyled.insertAfter($targetInputField)

  const validateROM = (arrayBuffer) => {
    const header = arrayBuffer.slice(0, 0x40)

    const endian_bytes = [header[0], header[1]]
    let endianess = 'unknown'

    if (endian_bytes.toString() == [0x80, 0x37].toString()) {
      endianess = 'big'
    } else if (endian_bytes.toString() == [0x37, 0x80].toString()) {
      endianess = 'mixed'
    } else if (endian_bytes.toString() == [0x40, 0x12].toString()) {
      endianess = 'little'
    } else {
      console.log(endian_bytes.toString())
      throw new Error('invalid endianess')
    }

    let internalName = String.fromCharCode.apply(null, new Uint8Array(header.slice(0x18, 0x3B)))
    internalName = internalName.replace(/[^A-Za-z0-9 ]+/g, '').trim()
    
    if (internalName != 'SUPER MARIO 64') {
      throw new Error('invalid internal name - must be a SM64 ROM')
    }

    return arrayBuffer
  }

  const tryCompress = async (file) => {
    const zipBlob = await (new Promise((callback) => {
      const zipWriter = zip.createWriter(new zip.BlobWriter(), (writerInstance) => {
        writerInstance.add(file.name, new zip.BlobReader(file), () => {
          writerInstance.close(callback)
        })
      })
    }))
    
    return zipBlob
  }

  const validateInput = async (files) => {
    if (files.length > 1) {
      throw new Error('Please only upload one file at a time')
    }

    binaryData = await (new Promise((resolve, reject) => {
      const fileReader = new FileReader()
      fileReader.onload = (e) => {
        binaryData = new Uint8Array(fileReader.result)
        resolve(binaryData)
      }
      fileReader.onerror = (e) => {
        reject(e)
      }
      fileReader.readAsArrayBuffer(files[0])
    }))

    await validateROM(binaryData)
  } 

  const updateInputStatus = (status, message) => {
    // clear everything
    $targetInputField.prop('disabled', false)
    $message = $fieldContainer.closest('.message').text('')
    $message.addClass(status)
    $message.text(message)

    const canChange = status === 'success' || status === 'error'
    $targetInputField.prop('disabled', !canChange)
  }

  $targetInputField.on('change', async function() {
    updateInputStatus('pending')

    let blob
    try {
      validateInput(this.files)
      blob = this.files[0]
    } catch (err) {
      return updateInputStatus('error', err.message)
    }

    let URL
    try {
      URL = window.webkitURL || window.mozURL || window.URL
      updateInputStatus('load', 'Compressing your ROM...')
      blob = await tryCompress(this.files[0])
      $fileInputStyled.text('✓ Valid ROM')
      updateInputStatus('success', 'Prepared your ROM for uploading!')  
    } catch (err) {
      console.error(err)
      $fileInputStyled.text('✓ Valid ROM')
      updateInputStatus('success', 'File prepared, but could not compress the data. Sorry!')
    }

    $realUpload.val(URL.createObjectURL(blob))
  })

})