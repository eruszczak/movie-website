var gulp = require('gulp');
var gulpIf = require('gulp-if');

var sass = require('gulp-sass');
var useref = require('gulp-useref');
var cssnano = require('gulp-cssnano');

var imagemin = require('gulp-imagemin');
var imageResize = require('gulp-image-resize');
var replace = require('gulp-replace');
var gutil = require('gulp-util');

var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var concatCss = require('gulp-concat-css');
var cleanCSS = require('gulp-clean-css');


gulp.task('sass', function() {
    return gulp.src('static/**/*.scss')
        .pipe(sass())
        .pipe(gulp.dest('../dist'))
});




gulp.task('useref', function(){
  return gulp.src('templates/base.html')
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

jsFiles = [
    'static/bower_components/jquery/dist/jquery.min.js',
    'static/bower_components/jquery-ui/jquery-ui.min.js',
    'static/bower_components/bootstrap/dist/js/bootstrap.min.js',
    'static/bower_components/bootstrap-select/dist/js/bootstrap-select.js',
    'static/bower_components/highcharts/highcharts.js',
    'static/bower_components/highcharts/modules/exporting.js',
    'static/js/scripts.js',
    'static/js/graphs.js',
    'static/js/modaldialog.js',
]

cssFiles = [
    'static/bower_components/jquery-ui/themes/base/jquery-ui.min.css',
    'static/bower_components/bootstrap/dist/css/bootstrap.min.css',
    'static/bower_components/bootstrap-select/dist/css/bootstrap-select.min.css',
	'static/css/styles.css'
]

//files.filter(function(f) {
//    return 'static/' + f;
//})

gulp.task('scripts', function() {
  return gulp.src(jsFiles)
    .pipe(concat('allscripts.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('../dist'));
});

gulp.task('styles', function () {
  return gulp.src(cssFiles)
    .pipe(concatCss('allstyles.min.css'))
    .pipe(cleanCSS({compatibility: 'ie8'}))
    .pipe(gulp.dest('../dist'));
});

gulp.task('static', ['styles', 'scripts']);



gulp.task('clearCache', function() {
  // Still pass the files to clear cache for
//  gulp.src('./lib/*.js')
//    .pipe(cache.clear());

  // Or, just call this for everything
  cache.clearAll();
});