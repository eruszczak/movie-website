var gulp = require('gulp');
var gulpIf = require('gulp-if');

var sass = require('gulp-sass');
var useref = require('gulp-useref');
var uglify = require('gulp-uglify');
var cssnano = require('gulp-cssnano');

var imagemin = require('gulp-imagemin');
var imageResize = require('gulp-image-resize');
var concat = require('gulp-concat');
var replace = require('gulp-replace');
var gutil = require('gulp-util');

gulp.task('sass', function() {
    return gulp.src('static/**/*.scss')
        .pipe(sass())
        .pipe(gulp.dest('../dist'))
});




gulp.task('useref', function(){
  return gulp.src('templates/base.html')
    .pipe(replace(/{% static/g, ''))
    .pipe(replace(/ %}/g, ''))
    .pipe(useref())
    .pipe(gulpIf('*.js', uglify().on('error', function(err) {
        gutil.log(gutil.colors.red('[Error]'), err.toString());
        this.emit('end');
        }))
     )
    .pipe(gulpIf('*.css', cssnano()))
    .pipe(gulp.dest('../dist'))
});

//gulp.watch('static/**/*.scss', ['sass']);

gulp.task('watch', function(){
    gulp.watch('static/**/*.scss', ['sass']);
});

gulp.task('images', function() {
    return gulp.src('../media/poster/*.+(png|jpg|gif|svg)')
    .pipe(imagemin())
    .pipe(gulp.dest('../dist/images'))
});

gulp.task('img', () =>
    gulp.src('../media/poster/*.+(png|jpg|gif|svg)')
        .pipe(imagemin())
        .pipe(imageResize({
            width: 120,
            crop: true,
            upscale: false
        }))
        .pipe(gulp.dest('../dist/images'))
);

//var files = [
//    'bower_components/jquery/dist/jquery.min.js'
//    'bower_components/jquery-ui/jquery-ui.min.js'
//    'bower_components/bootstrap/dist/js/bootstrap.min.js'
//    'bower_components/bootstrap-select/dist/js/bootstrap-select.js'
//    'bower_components/highcharts/highcharts.js'
//    'bower_components/highcharts/modules/exporting.js'
//    'js/scripts.js'
//    'js/graphs.js'
//]
//
//files.filter(function(f) {
//    return 'static/' + f;
//})
//
//gulp.task('scripts', function() {
//  return gulp.src(files)
//    .pipe(concat('all.js'))
//    .pipe(gulp.dest('static/js/'));
//});

gulp.task('clearCache', function() {
  // Still pass the files to clear cache for
//  gulp.src('./lib/*.js')
//    .pipe(cache.clear());

  // Or, just call this for everything
  cache.clearAll();
});