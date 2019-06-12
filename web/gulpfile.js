'use strict';
 
const { src, dest, task, watch, parallel } = require('gulp')
var sass = require('gulp-sass');
const mapStream = require('map-stream')
 
sass.compiler = require('node-sass');
 
const scssBuild = () => {
  return src('./scss/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(dest('../docs/css'));
};
 
const scssWatch = () => {
  watch('./scss/**/*.scss', scssBuild);
};

const copy = () => {
  return src(['./*.html', './assets/**/*', './*.ico'])
      .pipe(dest('../docs'))
}

const copyConfig = () => {
  return src('../Data/configurableParams.json')
    .pipe(mapStream((file, done) => {
      const json = file.contents.toString()
      const output = `${file.stem} = ${JSON.stringify(JSON.parse(json), null, 2)}`

      file.contents = Buffer.from(output)
      file.extname = '.js'

      done(null, file)
    }))
    .pipe(dest('../docs'))
}

const copyAll = () => {
  return parallel(copy, copyConfig)
}

const copyWatch = () => {
  watch(['./**/*.js', './**/*.html', '../Data/*.json'], copyAll)
}

exports.default = parallel(scssBuild, copy, copyConfig)
exports.watch = parallel(scssWatch, copyWatch)
exports.copyConfig = copyConfig